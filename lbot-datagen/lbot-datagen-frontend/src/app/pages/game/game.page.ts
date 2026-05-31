import {
  Component,
  OnInit,
  OnDestroy,
  ViewChild,
  HostListener,
  signal,
  computed,
  effect
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { GameStateService } from '../../services/game-state.service';
import { LevelConfigService } from '../../services/level-config.service';
import { LeaderboardService } from '../../services/leaderboard.service';
import { MessagesService } from '../../services/messages-service';
import { LevelConfig } from '../../models/level-config.model';
import { RoboSimulatorComponent } from '../../components/robo-simulator/robo-simulator';
import { LbotChat } from '../../components/lbot-chat/lbot-chat';
import { LevelTransitionComponent } from '../../components/level-transition/level-transition';
import { VictoryScreenComponent, VictorySavePayload } from '../../components/victory-screen/victory-screen';
import { ConfirmModalComponent } from '../../components/confirm-modal/confirm-modal';

/**
 * Main game page orchestrating the 3-D simulator, chat panel, HUD, overlays
 * and the entire game-state machine (levels 1-5).
 *
 * Responsibilities:
 *  - Start a new run on init (GameStateService.startRun())
 *  - Listen to levelCompleted from RoboSimulator → call completeLevel()
 *  - Show LevelTransition overlay when phase === 'level-complete'
 *  - Show VictoryScreen overlay when phase === 'run-complete'
 *  - Show ConfirmModal when the user tries to navigate away mid-run
 *  - Update the global HUD timer every second via setInterval
 *  - Intercept browser back/close while a run is active
 */
@Component({
  selector: 'app-game-page',
  standalone: true,
  imports: [
    CommonModule,
    RoboSimulatorComponent,
    LbotChat,
    LevelTransitionComponent,
    VictoryScreenComponent,
    ConfirmModalComponent
  ],
  templateUrl: './game.page.html',
  styleUrl: './game.page.css'
})
export class GamePage implements OnInit, OnDestroy {

  @ViewChild(RoboSimulatorComponent) simulator?: RoboSimulatorComponent;

  // ── reactive state ──────────────────────────────────────────────────────
  /** Current level config to pass down to the simulator. */
  currentLevelConfig = signal<LevelConfig | undefined>(undefined);

  /** Timer display string updated every second ("MM:SS"). */
  timerDisplay = signal<string>('00:00');

  /** Controls visibility of the confirm-exit modal. */
  showConfirmModal = signal<boolean>(false);

  /** Pending navigation URL — set before showing the confirm modal. */
  private pendingNavUrl: string | null = null;

  /** True while the leaderboard save HTTP request is in flight. */
  isSaving = signal<boolean>(false);

  /** Set when the leaderboard save fails. */
  saveError = signal<boolean>(false);

  /** Cached payload for retry after a failed save. */
  private pendingSavePayload: VictorySavePayload | null = null;

  /**
   * ChatId do run atual (null enquanto aguarda resposta do backend).
   * Usado para renderizar o LbotChat somente quando o chatId estiver disponivel
   * e garantir que um unico chatId e usado por run inteiro (todos os 5 niveis).
   */
  currentChatId = signal<string | null>(null);

  // ── derived ─────────────────────────────────────────────────────────────
  /** Names of all completed levels (for VictoryScreen). */
  levelNames = computed<string[]>(() =>
    this.levelConfig.getAllLevels().map(l => l.name)
  );

  /** Next level name (for LevelTransitionComponent). */
  nextLevelName = computed<string>(() => {
    const next = this.gameState.currentLevel() + 1;
    if (next > 5) return '';
    return this.levelConfig.getLevel(next).name;
  });

  /** Formatted time of the level that just completed (for LevelTransition). */
  lastLevelTimeFormatted = computed<string>(() => {
    const times = this.gameState.levelTimes();
    if (times.length === 0) return '00:00';
    return this.gameState.formatTime(times[times.length - 1]);
  });

  /** Level number that just completed (before nextLevel() advances the pointer). */
  completedLevelNumber = signal<number>(1);

  /** Name of the level that just completed. */
  completedLevelName = signal<string>('');

  // ── internals ───────────────────────────────────────────────────────────
  private timerInterval?: ReturnType<typeof setInterval>;

  constructor(
    public readonly gameState: GameStateService,
    private readonly levelConfig: LevelConfigService,
    private readonly leaderboardService: LeaderboardService,
    private readonly messagesService: MessagesService,
    private readonly router: Router
  ) {
    // Keep currentLevelConfig in sync with currentLevel signal.
    effect(() => {
      const level = this.gameState.currentLevel();
      if (this.gameState.isRunActive()) {
        this.currentLevelConfig.set(this.levelConfig.getLevel(level));
      }
    });
  }

  // ── lifecycle ───────────────────────────────────────────────────────────

  ngOnInit(): void {
    this.gameState.startRun();
    this.startTimer();
    this.startNewChatSession();
  }

  ngOnDestroy(): void {
    this.stopTimer();
  }

  // ── browser back / close guard ──────────────────────────────────────────

  @HostListener('window:beforeunload', ['$event'])
  onBeforeUnload(event: BeforeUnloadEvent): void {
    if (this.gameState.isRunActive()) {
      event.preventDefault();
    }
  }

  // ── event handlers ──────────────────────────────────────────────────────

  /** Called by the simulator when the robot reaches point B. */
  onLevelCompleted(): void {
    // Snapshot which level just finished before state advances.
    const finishedLevel = this.gameState.currentLevel();
    const finishedName = this.levelConfig.getLevel(finishedLevel).name;
    this.completedLevelNumber.set(finishedLevel);
    this.completedLevelName.set(finishedName);

    this.gameState.completeLevel();

    if (this.gameState.phase() === 'run-complete') {
      this.stopTimer();
    }
  }

  /** "Próximo Nível" button in LevelTransition overlay. */
  onNextLevel(): void {
    this.gameState.nextLevel();
    // Give Angular one tick to update currentLevel before the simulator
    // reacts via the effect above.
  }

  /** "Jogar Novamente" in VictoryScreen. */
  onPlayAgain(): void {
    // Destroi o LbotChat (currentChatId = null) para limpar o historico
    this.currentChatId.set(null);
    this.gameState.startRun();
    this.startTimer();
    // Cria novo chatId para o novo run
    this.startNewChatSession();
  }

  /** "Salvar no Leaderboard" in VictoryScreen — wired to backend. */
  onSaveLeaderboard(payload: VictorySavePayload): void {
    this.pendingSavePayload = payload;
    this.doSave(payload);
  }

  /** Retry after a failed save (called from the template). */
  onRetrySave(): void {
    if (this.pendingSavePayload) {
      this.doSave(this.pendingSavePayload);
    }
  }

  private doSave(payload: VictorySavePayload): void {
    this.isSaving.set(true);
    this.saveError.set(false);

    const [t1, t2, t3, t4, t5] = payload.levelTimes;
    this.leaderboardService.saveGameRun({
      nickname: payload.nickname,
      level1TimeMs: t1 ?? 0,
      level2TimeMs: t2 ?? 0,
      level3TimeMs: t3 ?? 0,
      level4TimeMs: t4 ?? 0,
      level5TimeMs: t5 ?? 0
    }).subscribe({
      next: () => {
        this.isSaving.set(false);
        this.pendingSavePayload = null;
        this.router.navigateByUrl('/leaderboard');
      },
      error: () => {
        this.isSaving.set(false);
        this.saveError.set(true);
      }
    });
  }

  /** "Reiniciar Posição" HUD button — resets robot, timer keeps running. */
  onResetRobot(): void {
    this.simulator?.resetRobot();
  }

  /** Triggered by clicks on links that could navigate away from the game. */
  tryNavigate(url: string): void {
    if (this.gameState.isRunActive()) {
      this.pendingNavUrl = url;
      this.showConfirmModal.set(true);
    } else {
      this.router.navigateByUrl(url);
    }
  }

  onConfirmExit(): void {
    this.showConfirmModal.set(false);
    this.gameState.resetRun();
    this.stopTimer();
    if (this.pendingNavUrl) {
      this.router.navigateByUrl(this.pendingNavUrl);
      this.pendingNavUrl = null;
    }
  }

  onCancelExit(): void {
    this.showConfirmModal.set(false);
    this.pendingNavUrl = null;
  }

  // ── chat session ─────────────────────────────────────────────────────────

  /**
   * Inicia uma nova sessao de chat no backend e armazena o chatId.
   * O LbotChat so e renderizado no template quando currentChatId nao for null.
   */
  private startNewChatSession(): void {
    this.messagesService.startChat().subscribe({
      next: (chat) => {
        this.currentChatId.set(chat.id);
        console.log('[GamePage] Chat session started:', chat.id);
      },
      error: (err) => {
        console.warn('[GamePage] Failed to start chat session. Chat will be unavailable.', err);
        // Mesmo sem chat, o jogo continua funcionando
      }
    });
  }

  // ── timer ────────────────────────────────────────────────────────────────

  private startTimer(): void {
    this.stopTimer();
    this.timerDisplay.set(
      this.gameState.formatTime(this.gameState.getGlobalElapsedMs())
    );
    this.timerInterval = setInterval(() => {
      this.timerDisplay.set(
        this.gameState.formatTime(this.gameState.getGlobalElapsedMs())
      );
    }, 1000);
  }

  private stopTimer(): void {
    if (this.timerInterval !== undefined) {
      clearInterval(this.timerInterval);
      this.timerInterval = undefined;
    }
  }
}

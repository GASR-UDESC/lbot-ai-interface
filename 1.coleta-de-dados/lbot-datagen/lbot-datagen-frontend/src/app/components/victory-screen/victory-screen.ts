import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule, Trophy } from 'lucide-angular';

/** Payload emitted when the player saves to the leaderboard. */
export interface VictorySavePayload {
  nickname: string;
  levelTimes: number[];
  totalTime: number;
}

/**
 * Full-screen overlay shown when the player completes all 5 levels.
 * Displays per-level times, total time, a nickname input and action buttons.
 */
@Component({
  selector: 'app-victory-screen',
  standalone: true,
  imports: [CommonModule, FormsModule, LucideAngularModule],
  templateUrl: './victory-screen.html',
  styleUrls: ['./victory-screen.css']
})
export class VictoryScreenComponent {
  public readonly TrophyIcon = Trophy;

  /** Time in milliseconds for each completed level (index 0 = level 1). */
  @Input() levelTimes: number[] = [];

  /** Display names for each level, in order (index 0 = level 1). */
  @Input() levelNames: string[] = [];

  /** True while the parent is saving to the backend. */
  @Input() isSaving = false;

  /** True when the last save attempt failed. */
  @Input() saveError = false;

  /** Emitted when the player clicks "Salvar no Leaderboard". */
  @Output() save = new EventEmitter<VictorySavePayload>();

  /** Emitted when the player clicks "Tentar novamente" after a failed save. */
  @Output() retrySave = new EventEmitter<void>();

  /** Emitted when the player clicks "Jogar Desafios Novamente". */
  @Output() playAgain = new EventEmitter<void>();

  nickname = '';

  get totalTime(): number {
    return this.levelTimes.reduce((acc, t) => acc + t, 0);
  }

  formatTime(ms: number): string {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  onSave(): void {
    const trimmed = this.nickname.trim();
    if (!trimmed) return;
    this.save.emit({
      nickname: trimmed,
      levelTimes: this.levelTimes,
      totalTime: this.totalTime
    });
  }

  onRetrySave(): void {
    this.retrySave.emit();
  }

  onPlayAgain(): void {
    this.playAgain.emit();
  }
}

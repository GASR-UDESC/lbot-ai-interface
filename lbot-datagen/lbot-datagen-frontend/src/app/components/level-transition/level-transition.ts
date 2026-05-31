import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Overlay shown between two levels when a level is completed.
 * Displays the completed level name, time achieved and the next level name.
 * Emits `nextLevel` when the player clicks "Próximo Nível".
 */
@Component({
  selector: 'app-level-transition',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './level-transition.html',
  styleUrls: ['./level-transition.css']
})
export class LevelTransitionComponent {
  /** Number of the completed level (1-based). */
  @Input() levelNumber: number = 1;

  /** Display name of the completed level. */
  @Input() levelName: string = '';

  /** Time taken to complete the level in MM:SS format. */
  @Input() levelTime: string = '00:00';

  /** Display name of the next level. */
  @Input() nextLevelName: string = '';

  /** Emitted when the player clicks "Próximo Nível". */
  @Output() nextLevel = new EventEmitter<void>();

  onNextLevel(): void {
    this.nextLevel.emit();
  }
}

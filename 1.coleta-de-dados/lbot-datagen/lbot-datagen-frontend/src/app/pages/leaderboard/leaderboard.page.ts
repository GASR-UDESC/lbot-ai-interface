import { Component, OnInit, signal } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { LeaderboardService } from '../../services/leaderboard.service';
import { GameRunResponse } from '../../models/leaderboard.model';
import { LucideAngularModule, Trophy, TriangleAlert, Gamepad2, Medal } from 'lucide-angular';

/**
 * Leaderboard page — displays the global ranking of completed game runs
 * ordered by total time. Handles loading, empty and error states.
 */
@Component({
  selector: 'app-leaderboard-page',
  standalone: true,
  imports: [CommonModule, DatePipe, LucideAngularModule],
  templateUrl: './leaderboard.page.html',
  styleUrl: './leaderboard.page.css'
})
export class LeaderboardPage implements OnInit {

  public readonly TrophyIcon = Trophy;
  public readonly TriangleAlertIcon = TriangleAlert;
  public readonly GamepadIcon = Gamepad2;
  public readonly MedalIcon = Medal;

  /** Ordered list of game runs fetched from the backend. */
  entries = signal<GameRunResponse[]>([]);

  /** True while the HTTP request is in flight. */
  isLoading = signal<boolean>(true);

  /** Set when the backend is unreachable or returns an error. */
  hasError = signal<boolean>(false);

  constructor(private readonly leaderboardService: LeaderboardService) {}

  ngOnInit(): void {
    this.loadLeaderboard();
  }

  loadLeaderboard(): void {
    this.isLoading.set(true);
    this.hasError.set(false);

    this.leaderboardService.getLeaderboard().subscribe({
      next: (data) => {
        const parsed = data.map((entry) => {
          const [year, month, day, hour, minute, second] = entry.completedAt as unknown as number[];
          return {
            ...entry,
            completedAt: new Date(year, month - 1, day, hour, minute, second).toISOString()
          };
        });
        this.entries.set(parsed);
        this.isLoading.set(false);
      },
      error: () => {
        this.hasError.set(true);
        this.isLoading.set(false);
      }
    });
  }

  /**
   * Formats a duration in milliseconds to "MM:SS".
   */
  formatTime(ms: number): string {
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
}

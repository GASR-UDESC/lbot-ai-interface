import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Leaderboard page skeleton component.
 * Will be fully implemented in Phase 06 (Frontend Leaderboard & Integration).
 */
@Component({
  selector: 'app-leaderboard-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './leaderboard.page.html',
  styleUrl: './leaderboard.page.css'
})
export class LeaderboardPage {}

import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Game page skeleton component.
 * Will be fully implemented in Phase 04 (Game UI).
 */
@Component({
  selector: 'app-game-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './game.page.html',
  styleUrl: './game.page.css'
})
export class GamePage {}

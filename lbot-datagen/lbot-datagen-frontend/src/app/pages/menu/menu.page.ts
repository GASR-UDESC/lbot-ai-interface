import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Main menu page component.
 * Entry point of the application: allows navigation to game, leaderboard, and controls mode.
 */
@Component({
  selector: 'app-menu-page',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './menu.page.html',
  styleUrl: './menu.page.css'
})
export class MenuPage {}

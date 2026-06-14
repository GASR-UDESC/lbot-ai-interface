import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { LucideAngularModule, Play, Trophy, Gamepad2, Bot } from 'lucide-angular';

/**
 * Main menu page component.
 * Entry point of the application: allows navigation to game, leaderboard, and controls mode.
 */
@Component({
  selector: 'app-menu-page',
  standalone: true,
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './menu.page.html',
  styleUrl: './menu.page.css'
})
export class MenuPage {
  public readonly PlayIcon = Play;
  public readonly TrophyIcon = Trophy;
  public readonly GamepadIcon = Gamepad2;
  public readonly BotIcon = Bot;
}

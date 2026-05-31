import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/menu',
    pathMatch: 'full'
  },
  {
    path: 'menu',
    loadComponent: () =>
      import('./pages/menu/menu.page').then(m => m.MenuPage)
  },
  {
    path: 'game',
    loadComponent: () =>
      import('./pages/game/game.page').then(m => m.GamePage)
  },
  {
    path: 'leaderboard',
    loadComponent: () =>
      import('./pages/leaderboard/leaderboard.page').then(m => m.LeaderboardPage)
  },
  {
    path: 'controls',
    loadComponent: () =>
      import('./pages/controls/controls.page').then(m => m.ControlsPage)
  },
  {
    path: '**',
    redirectTo: '/menu'
  }
];

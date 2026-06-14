import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  // WebGL pages: must NOT be prerendered (THREE.js / CANNON cannot run in Node).
  {
    path: 'game',
    renderMode: RenderMode.Client
  },
  {
    path: 'controls',
    renderMode: RenderMode.Client
  },
  // Menu & leaderboard: lucide-angular icons use imperative DOM manipulation
  // that does not replay correctly during SSR hydration. Render client-side
  // so the SVG injection always runs in the browser.
  {
    path: 'menu',
    renderMode: RenderMode.Client
  },
  {
    path: 'leaderboard',
    renderMode: RenderMode.Client
  },
  {
    path: '**',
    renderMode: RenderMode.Prerender
  }
];

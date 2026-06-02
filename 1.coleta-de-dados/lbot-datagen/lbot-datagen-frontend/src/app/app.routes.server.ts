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
  {
    path: '**',
    renderMode: RenderMode.Prerender
  }
];

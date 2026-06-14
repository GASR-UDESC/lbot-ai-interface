import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, Router, NavigationEnd } from '@angular/router';
import { LucideAngularModule, ArrowLeft } from 'lucide-angular';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-back-button',
  imports: [CommonModule, RouterLink, LucideAngularModule],
  templateUrl: './back-button.html',
  styleUrl: './back-button.css',
  standalone: true
})
export class BackButtonComponent {
  private router = inject(Router);
  readonly ArrowLeftIcon = ArrowLeft;
  showBack = true;

  constructor() {
    this.showBack = this.router.url !== '/menu';
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd)
    ).subscribe(() => {
      this.showBack = this.router.url !== '/menu';
    });
  }
}

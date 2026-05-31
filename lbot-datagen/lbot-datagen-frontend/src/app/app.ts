import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

/**
 * Root component of the LBot DataGen application.
 * Renders the router outlet for multi-page navigation.
 */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css',
  standalone: true
})
export class AppComponent {}

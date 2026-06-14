import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { BackButtonComponent } from './components/back-button/back-button';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, BackButtonComponent],
  templateUrl: './app.html',
  styleUrl: './app.css',
  standalone: true
})
export class AppComponent {}

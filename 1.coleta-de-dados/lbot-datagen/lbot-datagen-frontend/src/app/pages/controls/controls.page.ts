import { Component } from '@angular/core';
import { RoboSimulatorComponent } from '../../components/robo-simulator/robo-simulator';
import { VirtualControlsComponent } from '../../components/virtual-controls/virtual-controls';

/**
 * Controls page component.
 * Embeds the robot simulator with virtual directional controls for data generation.
 * This is the standalone "Modo Controle" accessible from the main menu.
 */
@Component({
  selector: 'app-controls-page',
  standalone: true,
  imports: [RoboSimulatorComponent, VirtualControlsComponent],
  templateUrl: './controls.page.html',
  styleUrl: './controls.page.css'
})
export class ControlsPage {}

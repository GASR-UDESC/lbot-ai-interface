import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Generic confirmation modal with backdrop.
 * Fully reusable — configure title/message/button labels via inputs.
 */
@Component({
  selector: 'app-confirm-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './confirm-modal.html',
  styleUrls: ['./confirm-modal.css']
})
export class ConfirmModalComponent {
  @Input() title: string = 'Tem certeza?';
  @Input() message: string = 'Você vai perder todo o progresso do jogo. Tem certeza?';
  @Input() confirmText: string = 'Sim, sair';
  @Input() cancelText: string = 'Cancelar';

  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  onConfirm(): void {
    this.confirm.emit();
  }

  onCancel(): void {
    this.cancel.emit();
  }
}

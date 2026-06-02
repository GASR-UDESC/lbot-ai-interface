import { Component, OnInit, OnDestroy, OnChanges, Input, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatDto, MessageDto, MessagesService } from '../../services/messages-service';
import { SimulatorBridgeService } from '../../services/simulator-bridge.service';
import { LucideAngularModule, Bot, Star } from 'lucide-angular';

/**
 * Message types supported by the chat interface.
 */
type MessageType = 'user' | 'bot' | 'error' | 'system';

/**
 * Represents a chat message in the interface.
 */
interface ChatMessage {
  text: string;
  type: MessageType;
  messageId?: string;
  normalizedPrompt?: string;
  output?: string;
  rated?: boolean;
  rating?: number;
}

interface PendingReevaluation {
  messageId: string;
  rating: number;
}

/**
 * Star rating configuration.
 */
interface StarRating {
  value: number;
  title: string;
  emoji: string;
}

/**
 * Chat component that handles the conversation interface with the LBot translator.
 * Manages message sending, rating, and chat lifecycle.
 */
@Component({
  selector: 'app-lbot-chat',
  standalone: true,
  imports: [CommonModule, FormsModule, LucideAngularModule],
  templateUrl: './lbot-chat.html',
  styleUrls: ['./lbot-chat.css']
})
export class LbotChat implements OnInit, OnDestroy, OnChanges {
  public readonly stars = [1, 2, 3, 4, 5];

  // ── Inputs para modo gamificado ──────────────────────────────────────────
  /** Se fornecido, o chat usa este chatId (nao cria um novo via startChat). */
  @Input() externalChatId?: string;
  /** Se true, esconde o botao "Encerrar" (modo jogo: o ciclo de vida e gerenciado pelo GamePage). */
  @Input() gameMode: boolean = false;
  /** Nome do nivel atual (modo jogo). Quando muda, insere um banner de sistema no chat. */
  @Input() currentLevelName?: string;

  private static readonly INITIAL_MESSAGE: ChatMessage = {
    text: 'Olá! Digite um comando em português e eu traduzo para LBML.',
    type: 'bot'
  };

  private static readonly STAR_RATINGS: ReadonlyArray<StarRating> = [
    { value: 1, title: 'Muito ruim', emoji: '⭐' },
    { value: 2, title: 'Ruim', emoji: '⭐' },
    { value: 3, title: 'Ok', emoji: '⭐' },
    { value: 4, title: 'Bom', emoji: '⭐' },
    { value: 5, title: 'Excelente', emoji: '⭐' }
  ];

  private static readonly FAREWELL_DELAY_MS = 2000;
  private static readonly CHAT_CLEAR_DELAY_MS = 2000;

  // Public state
  public messages: ChatMessage[] = [LbotChat.INITIAL_MESSAGE];
  public messageInput = '';
  public isLoading = false;
  public showObservation = false;
  public observation = '';
  public showReevaluationPopup = false;
  
  // Icons
  public readonly BotIcon = Bot;
  public readonly StarIcon = Star;

  // Private state
  private readonly ratings = new Map<string, number>();
  private chatId = '';
  private pendingReevaluation: PendingReevaluation | null = null;

  constructor(
    private readonly messagesService: MessagesService,
    private readonly simulatorBridge: SimulatorBridgeService
  ) { }

  public ngOnChanges(changes: SimpleChanges): void {
    // Insere banner de nivel quando currentLevelName muda (nao na primeira renderizacao)
    if (changes['currentLevelName'] && !changes['currentLevelName'].isFirstChange()) {
      const levelName = changes['currentLevelName'].currentValue as string | undefined;
      if (levelName) {
        this.addSystemMessage(`— Nível: ${levelName} —`);
      }
    }
  }

  public ngOnInit(): void {
    this.initializeChat();
  }

  public ngOnDestroy(): void {
    // Cleanup if necessary
  }

  /**
   * Initializes a new chat session with the backend.
   * In game mode, uses the externalChatId provided by the parent component.
   */
  private initializeChat(): void {
    if (this.externalChatId) {
      // Modo gamificado: usar chatId externo fornecido pelo GamePage
      this.chatId = this.externalChatId;
      console.log('[LbotChat] Using external chat ID:', this.chatId);
      return;
    }

    this.messagesService.startChat().subscribe({
      next: (response: ChatDto) => {
        this.chatId = response.id;
        console.log('[LbotChat] Chat initialized:', {
          id: this.chatId,
          createdAt: response.createdAt
        });
      },
      error: (error: unknown) => {
        console.error('[LbotChat] Failed to initialize chat:', error);
        this.addErrorMessage('Erro ao iniciar o chat. Tente novamente.');
      }
    });
  }

  /**
   * Sends a message to the backend and updates the UI accordingly.
   */
  public sendMessage(): void {
    const command = this.messageInput.trim();
    
    if (!this.canSendMessage(command)) {
      return;
    }

    this.prepareMessageSending(command);
    this.sendMessageToBackend(command);
  }

  /**
   * Handles Enter key press to send message.
   */
  public onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      this.sendMessage();
    }
  }

  /**
   * Returns the title for a star rating value.
   */
  public getStarTitle(star: number): string {
    const starRating = LbotChat.STAR_RATINGS.find(sr => sr.value === star);
    return starRating?.title ?? 'Avaliar';
  }

  /**
   * Returns the emoji for a rating value.
   */
  public getRatingEmoji(rating: number): string {
    const starRating = LbotChat.STAR_RATINGS.find(sr => sr.value === rating);
    return starRating?.emoji ?? '�';
  }

  /**
   * Rates a message with stars.
   */
  public quickRate(messageId: string, rating: number, event?: MouseEvent | TouchEvent): void {
    event?.stopPropagation();

    const message = this.messages.find(m => m.messageId === messageId);

    if (!message) {
      return;
    }

    if (message.rating === rating) {
      return;
    }

    if (message.rated) {
      this.pendingReevaluation = { messageId, rating };
      this.showReevaluationPopup = true;
      return;
    }

    this.updateMessageRating(messageId, rating);
    this.submitRatingToBackend(messageId, rating);
  }

  /**
   * Returns whether a star should be shown as selected.
   */
  public isStarFilled(message: ChatMessage, star: number): boolean {
    return (message.rating ?? 0) >= star;
  }

  /**
   * Closes the reevaluation popup without changing the current rating.
   */
  public closeReevaluationPopup(): void {
    this.showReevaluationPopup = false;
    this.pendingReevaluation = null;
  }

  /**
   * Confirms and submits a reevaluation.
   */
  public confirmReevaluation(): void {
    if (!this.pendingReevaluation) {
      return;
    }

    const { messageId, rating } = this.pendingReevaluation;
    this.closeReevaluationPopup();
    this.updateMessageRating(messageId, rating);
    this.submitRatingToBackend(messageId, rating);
  }

  /**
   * Shows the observation popup when user wants to end the chat.
   */
  public showObservationPopup(): void {
    this.showObservation = true;
    this.observation = '';
  }

  /**
   * Closes the observation popup without submitting.
   */
  public closeObservationPopup(): void {
    this.showObservation = false;
    this.observation = '';
  }

  /**
   * Submits final observations and ends the chat session.
   */
  public submitObservation(): void {
    this.displayFinalFeedback();
    this.closeObservationPopup();
    this.scheduleChatCleanup();
  }

  /**
   * Checks if a message can be sent.
   */
  private canSendMessage(command: string): boolean {
    return !!(command && !this.isLoading && this.chatId);
  }

  /**
   * Prepares the UI for sending a message.
   */
  private prepareMessageSending(command: string): void {
    this.messages.push({ text: command, type: 'user' });
    this.messageInput = '';
    this.isLoading = true;
    this.scrollToBottom();
  }

  /**
   * Sends the message to the backend API.
   */
  private sendMessageToBackend(command: string): void {
    this.messagesService.sendMessage({
      prompt: command,
      chatId: this.chatId
    }).subscribe({
      next: (response: MessageDto) => this.handleMessageSuccess(response),
      error: (error: unknown) => this.handleMessageError(error)
    });
  }

  /**
   * Handles successful message response from backend.
   */
  private handleMessageSuccess(response: MessageDto): void {
    console.log('[LbotChat] Message response:', response);

    const botMessage: ChatMessage = {
      text: response.output || 'Comando processado com sucesso!',
      type: 'bot',
      messageId: response.id,
      normalizedPrompt: response.normalizedPrompt,
      output: response.output,
      rated: response.grade !== null,
      rating: response.grade ?? undefined
    };

    this.messages.push(botMessage);
    this.isLoading = false;
    this.scrollToBottom();

    if (response.output) {
      this.simulatorBridge.executeLbml(response.output);
    }
  }

  /**
   * Handles message sending error.
   */
  private handleMessageError(error: unknown): void {
    console.error('[LbotChat] Failed to send message:', error);
    this.addErrorMessage('Erro ao processar sua mensagem. Tente novamente.');
    this.isLoading = false;
    this.scrollToBottom();
  }

  /**
   * Updates the rating for a specific message in the UI.
   */
  private updateMessageRating(messageId: string, rating: number): void {
    const message = this.messages.find(m => m.messageId === messageId);
    
    if (message) {
      message.rated = true;
      message.rating = rating;
    }

    this.ratings.set(messageId, rating);
  }

  /**
   * Submits a rating to the backend API.
   */
  private submitRatingToBackend(messageId: string, rating: number): void {
    this.messagesService.evaluateMessage({
      messageId,
      grade: rating
    }).subscribe({
      next: (response: MessageDto) => {
        console.log('[LbotChat] Rating submitted:', { messageId, rating, response });
        this.updateMessageRating(messageId, response.grade ?? rating);
      },
      error: (error: unknown) => {
        console.error('[LbotChat] Failed to submit rating:', error);
      }
    });
  }

  /**
   * Displays final feedback message to the user.
   */
  private displayFinalFeedback(): void {
    const finalFeedback = this.buildFinalFeedback();
    console.log('[LbotChat] Final feedback:', finalFeedback);

    const thankYouMessage = this.buildThankYouMessage(finalFeedback.averageRating);
    this.messages.push({ text: thankYouMessage, type: 'bot' });
    this.scrollToBottom();
  }

  /**
   * Builds the final feedback object with all ratings and observations.
   */
  private buildFinalFeedback() {
    const averageRating = this.calculateAverageRating();

    return {
      chatId: this.chatId,
      individualRatings: Array.from(this.ratings.values()),
      averageRating,
      totalMessages: this.ratings.size,
      observation: this.observation.trim()
    };
  }

  /**
   * Calculates the average rating from all submitted ratings.
   */
  private calculateAverageRating(): string {
    if (this.ratings.size === 0) {
      return 'N/A';
    }

    const ratings = Array.from(this.ratings.values());
    const sum = ratings.reduce((acc, rating) => acc + rating, 0);
    const average = sum / ratings.length;
    return average.toFixed(1);
  }

  /**
   * Builds a personalized thank you message based on feedback.
   */
  private buildThankYouMessage(averageRating: string): string {
    let message = 'Obrigado pelo feedback! ';

    if (this.ratings.size > 0) {
      const pluralMessages = this.ratings.size > 1 ? 's' : '';
      const pluralEvaluated = this.ratings.size > 1 ? 's' : '';
      message += `Média das avaliações: ${averageRating} estrelas (${this.ratings.size} mensagem${pluralMessages} avaliada${pluralEvaluated}). `;
    }

    if (this.observation.trim()) {
      message += 'Suas observações foram registradas.';
    }

    return message;
  }

  /**
   * Schedules chat cleanup after showing farewell message.
   */
  private scheduleChatCleanup(): void {
    setTimeout(() => {
      this.messages.push({
        text: 'Chat finalizado. Até a próxima!',
        type: 'bot'
      });
      this.scrollToBottom();

      setTimeout(() => {
        this.clearChat();
      }, LbotChat.CHAT_CLEAR_DELAY_MS);
    }, LbotChat.FAREWELL_DELAY_MS);
  }

  /**
   * Clears chat state and reinitializes.
   */
  private clearChat(): void {
    this.messages = [LbotChat.INITIAL_MESSAGE];
    this.messageInput = '';
    this.isLoading = false;
    this.showObservation = false;
    this.observation = '';
    this.closeReevaluationPopup();
    this.ratings.clear();
    this.chatId = '';

    this.initializeChat();
    console.log('[LbotChat] Chat cleared and reinitialized');
  }

  /**
   * Adds a system/informational message to the chat (not sent to backend).
   */
  private addSystemMessage(text: string): void {
    this.messages.push({ text, type: 'system' });
    this.scrollToBottom();
  }

  /**
   * Adds an error message to the chat.
   */
  private addErrorMessage(text: string): void {
    this.messages.push({ text, type: 'error' });
  }

  /**
   * Scrolls the chat messages container to the bottom.
   */
  private scrollToBottom(): void {
    setTimeout(() => {
      const messagesContainer = document.querySelector('.chat-messages');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);
  }
}

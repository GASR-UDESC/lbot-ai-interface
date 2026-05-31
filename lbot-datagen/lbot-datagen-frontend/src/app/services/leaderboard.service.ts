import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { CreateGameRunRequest, GameRunResponse } from '../models/leaderboard.model';

/**
 * Service responsible for communicating with the leaderboard API.
 * Handles saving game runs and fetching the global ranking.
 */
@Injectable({
  providedIn: 'root'
})
export class LeaderboardService {
  private readonly baseUrl = environment.apiBaseUrl;
  private readonly defaultHeaders = new HttpHeaders({
    'Content-Type': 'application/json'
  });

  constructor(private readonly http: HttpClient) {}

  /**
   * Saves a completed game run to the leaderboard.
   * @param request - The game run data including nickname and per-level times
   * @returns Observable with the created game run entry
   */
  public saveGameRun(request: CreateGameRunRequest): Observable<GameRunResponse> {
    return this.http.post<GameRunResponse>(
      `${this.baseUrl}/game-runs`,
      request,
      { headers: this.defaultHeaders }
    );
  }

  /**
   * Fetches the global leaderboard ordered by total time (ascending).
   * @returns Observable with the list of game run entries
   */
  public getLeaderboard(): Observable<GameRunResponse[]> {
    return this.http.get<GameRunResponse[]>(
      `${this.baseUrl}/game-runs`,
      { headers: this.defaultHeaders }
    );
  }
}

package br.com.roselabs.lbot_datagen_backend.controllers;

import br.com.roselabs.lbot_datagen_backend.dtos.CreateGameRunRequest;
import br.com.roselabs.lbot_datagen_backend.dtos.GameRunResponse;
import br.com.roselabs.lbot_datagen_backend.services.GameRunService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/game-runs")
@RequiredArgsConstructor
public class GameRunController {

    private final GameRunService gameRunService;

    @PostMapping
    public ResponseEntity<GameRunResponse> createGameRun(
            @RequestBody @Valid CreateGameRunRequest request) {
        try {
            GameRunResponse response = gameRunService.createGameRun(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        }
    }

    @GetMapping
    public ResponseEntity<List<GameRunResponse>> getAllGameRuns() {
        try {
            List<GameRunResponse> runs = gameRunService.getAllGameRuns();
            return ResponseEntity.ok(runs);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}

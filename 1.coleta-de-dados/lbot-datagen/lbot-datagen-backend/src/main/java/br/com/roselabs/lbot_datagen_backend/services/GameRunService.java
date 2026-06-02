package br.com.roselabs.lbot_datagen_backend.services;

import br.com.roselabs.lbot_datagen_backend.dtos.CreateGameRunRequest;
import br.com.roselabs.lbot_datagen_backend.dtos.GameRunResponse;
import br.com.roselabs.lbot_datagen_backend.entities.GameRun;
import br.com.roselabs.lbot_datagen_backend.repositories.GameRunRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class GameRunService {

    private final GameRunRepository gameRunRepository;

    @Transactional
    public GameRunResponse createGameRun(CreateGameRunRequest request) {
        long totalTimeMs = request.getLevel1TimeMs()
                + request.getLevel2TimeMs()
                + request.getLevel3TimeMs()
                + request.getLevel4TimeMs()
                + request.getLevel5TimeMs();

        GameRun gameRun = GameRun.builder()
                .nickname(request.getNickname())
                .level1TimeMs(request.getLevel1TimeMs())
                .level2TimeMs(request.getLevel2TimeMs())
                .level3TimeMs(request.getLevel3TimeMs())
                .level4TimeMs(request.getLevel4TimeMs())
                .level5TimeMs(request.getLevel5TimeMs())
                .totalTimeMs(totalTimeMs)
                .completedAt(LocalDateTime.now())
                .build();

        GameRun saved = gameRunRepository.save(gameRun);
        return new GameRunResponse(saved);
    }

    @Transactional(readOnly = true)
    public List<GameRunResponse> getAllGameRuns() {
        return gameRunRepository.findAllByOrderByTotalTimeMsAsc()
                .stream()
                .map(GameRunResponse::new)
                .collect(Collectors.toList());
    }
}

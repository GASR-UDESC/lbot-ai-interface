package br.com.roselabs.lbot_datagen_backend.dtos;

import br.com.roselabs.lbot_datagen_backend.entities.GameRun;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;
import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class GameRunResponse {

    private UUID id;
    private String nickname;
    private Long level1TimeMs;
    private Long level2TimeMs;
    private Long level3TimeMs;
    private Long level4TimeMs;
    private Long level5TimeMs;
    private Long totalTimeMs;
    private LocalDateTime completedAt;

    public GameRunResponse(GameRun gameRun) {
        this.id = gameRun.getId();
        this.nickname = gameRun.getNickname();
        this.level1TimeMs = gameRun.getLevel1TimeMs();
        this.level2TimeMs = gameRun.getLevel2TimeMs();
        this.level3TimeMs = gameRun.getLevel3TimeMs();
        this.level4TimeMs = gameRun.getLevel4TimeMs();
        this.level5TimeMs = gameRun.getLevel5TimeMs();
        this.totalTimeMs = gameRun.getTotalTimeMs();
        this.completedAt = gameRun.getCompletedAt();
    }
}

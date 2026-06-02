package br.com.roselabs.lbot_datagen_backend.entities;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.*;
import org.hibernate.annotations.GenericGenerator;

import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "game_runs")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GameRun {

    @Id
    @GeneratedValue(generator = "UUID")
    @GenericGenerator(name = "UUID", strategy = "org.hibernate.id.UUIDGenerator")
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @NotBlank
    @Column(name = "nickname", nullable = false)
    private String nickname;

    @NotNull
    @Column(name = "level1_time_ms", nullable = false)
    private Long level1TimeMs;

    @NotNull
    @Column(name = "level2_time_ms", nullable = false)
    private Long level2TimeMs;

    @NotNull
    @Column(name = "level3_time_ms", nullable = false)
    private Long level3TimeMs;

    @NotNull
    @Column(name = "level4_time_ms", nullable = false)
    private Long level4TimeMs;

    @NotNull
    @Column(name = "level5_time_ms", nullable = false)
    private Long level5TimeMs;

    @Column(name = "total_time_ms", nullable = false)
    private Long totalTimeMs;

    @Column(name = "completed_at", nullable = false)
    @Builder.Default
    private LocalDateTime completedAt = LocalDateTime.now();
}

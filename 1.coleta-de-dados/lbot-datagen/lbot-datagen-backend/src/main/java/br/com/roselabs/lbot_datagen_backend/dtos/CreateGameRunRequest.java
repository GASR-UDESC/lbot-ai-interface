package br.com.roselabs.lbot_datagen_backend.dtos;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class CreateGameRunRequest {

    @NotBlank
    private String nickname;

    @NotNull
    private Long level1TimeMs;

    @NotNull
    private Long level2TimeMs;

    @NotNull
    private Long level3TimeMs;

    @NotNull
    private Long level4TimeMs;

    @NotNull
    private Long level5TimeMs;
}

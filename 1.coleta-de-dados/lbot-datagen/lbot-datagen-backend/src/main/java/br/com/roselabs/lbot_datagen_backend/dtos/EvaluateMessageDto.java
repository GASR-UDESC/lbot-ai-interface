package br.com.roselabs.lbot_datagen_backend.dtos;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.util.UUID;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class EvaluateMessageDto {

    @NotNull
    private UUID messageId;

    @NotNull
    @Min(1)
    @Max(5)
    private Integer grade;
}

package br.com.roselabs.lbot_datagen_backend.dtos;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDescriptionRequestDTO {

    private String movementDescription;
}

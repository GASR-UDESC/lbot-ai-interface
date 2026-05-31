package br.com.roselabs.lbot_datagen_backend.controllers;

import br.com.roselabs.lbot_datagen_backend.dtos.EvaluateMessageDto;
import br.com.roselabs.lbot_datagen_backend.dtos.MessageDto;
import br.com.roselabs.lbot_datagen_backend.dtos.SendMessageDto;
import br.com.roselabs.lbot_datagen_backend.services.MessageService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PathVariable;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("messages")
@RequiredArgsConstructor
public class MessageController {

    private final MessageService messageService;

    @PostMapping
    public ResponseEntity<MessageDto> sendMessage(@RequestBody SendMessageDto sendMessageDto) {
        try {
            MessageDto createdMessage = messageService.sendMessage(sendMessageDto);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdMessage);
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PostMapping("evaluate")
    public ResponseEntity<MessageDto> evaluateMessage(@Valid @RequestBody EvaluateMessageDto evaluateMessageDto) {
        return upsertMessageEvaluation(evaluateMessageDto);
    }

    @PutMapping("{messageId}/evaluation")
    public ResponseEntity<MessageDto> reevaluateMessage(
            @PathVariable UUID messageId,
            @Valid @RequestBody EvaluateMessageDto evaluateMessageDto
    ) {
        evaluateMessageDto.setMessageId(messageId);
        return upsertMessageEvaluation(evaluateMessageDto);
    }

    private ResponseEntity<MessageDto> upsertMessageEvaluation(EvaluateMessageDto evaluateMessageDto) {
        try {
            MessageDto createdMessage = messageService.evaluateMessage(evaluateMessageDto);
            return ResponseEntity.status(HttpStatus.ACCEPTED).body(createdMessage);
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @org.springframework.web.bind.annotation.ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidationError(MethodArgumentNotValidException exception) {
        return ResponseEntity.badRequest().body(Map.of("message", "A nota deve estar entre 1 e 5."));
    }

}

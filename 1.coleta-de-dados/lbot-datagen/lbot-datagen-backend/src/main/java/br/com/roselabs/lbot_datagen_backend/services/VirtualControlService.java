package br.com.roselabs.lbot_datagen_backend.services;

import br.com.roselabs.lbot_datagen_backend.dtos.CreateVirtualControlSessionDTO;
import br.com.roselabs.lbot_datagen_backend.dtos.ValidateDescriptionResponseDTO;
import br.com.roselabs.lbot_datagen_backend.dtos.VirtualControlSessionDTO;
import br.com.roselabs.lbot_datagen_backend.entities.VirtualControlCommand;
import br.com.roselabs.lbot_datagen_backend.entities.VirtualControlSession;
import br.com.roselabs.lbot_datagen_backend.repositories.VirtualControlSessionRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class VirtualControlService {

    private final VirtualControlSessionRepository sessionRepository;
    private final AIService aiService;

    @Transactional
    public VirtualControlSessionDTO createSession(CreateVirtualControlSessionDTO createDto) {
        // Create session entity
        VirtualControlSession session = VirtualControlSession.builder()
                .movementDescription(createDto.getMovementDescription())
                .lbmlCommand(createDto.getLbmlCommand())
                .executedAt(LocalDateTime.now())
                .build();

        // Create and add commands
        if (createDto.getCommands() != null) {
            for (CreateVirtualControlSessionDTO.CreateVirtualControlCommandDTO cmdDto : createDto.getCommands()) {
                VirtualControlCommand command = VirtualControlCommand.builder()
                        .commandType(cmdDto.getCommandType())
                        .value(cmdDto.getValue())
                        .direction(cmdDto.getDirection())
                        .description(cmdDto.getDescription())
                        .sequenceOrder(cmdDto.getSequenceOrder())
                        .build();
                session.addCommand(command);
            }
        }

        // Save and return
        VirtualControlSession savedSession = sessionRepository.save(session);
        return new VirtualControlSessionDTO(savedSession);
    }

    @Transactional(readOnly = true)
    public List<VirtualControlSessionDTO> getAllSessions() {
        return sessionRepository.findAll().stream()
                .map(VirtualControlSessionDTO::new)
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public VirtualControlSessionDTO getSessionById(UUID id) {
        VirtualControlSession session = sessionRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Virtual Control Session not found with id: " + id));
        return new VirtualControlSessionDTO(session);
    }

    @Transactional(readOnly = true)
    public ValidateDescriptionResponseDTO validateDescription(String movementDescription) {
        boolean isValid = aiService.validateMovementDescription(movementDescription);

        if (isValid) {
            return new ValidateDescriptionResponseDTO(true, "Descrição válida.");
        } else {
            return new ValidateDescriptionResponseDTO(false,
                    "A descrição não parece descrever um movimento válido. " +
                    "Por favor, descreva um movimento que o robô possa realizar (ex: andar, girar, deslocar).");
        }
    }
}

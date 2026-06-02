package br.com.roselabs.lbot_datagen_backend.repositories;

import br.com.roselabs.lbot_datagen_backend.entities.GameRun;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface GameRunRepository extends JpaRepository<GameRun, UUID> {

    List<GameRun> findAllByOrderByTotalTimeMsAsc();
}

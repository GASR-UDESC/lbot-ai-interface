import type { AppConfig } from "../config";
import { createCliRuntime, type CliRuntime } from "./runtime";
import { createProcessingFeedback, type ProcessingFeedback } from "./processing-feedback";
import {
  completeCliTurn,
  formatPlannerError,
  isExitCommand,
  prepareCliTurn,
  spokenPlannerError,
} from "./turn";
import { VoiceBridgeProcessClient } from "../voice/process-client";

export interface VoiceClient {
  listenOnce(): Promise<{
    transcript: string;
    timedOut: boolean;
    heardSpeech: boolean;
  }>;
  speak(text: string): Promise<void>;
  dispose?: () => void | Promise<void>;
}

function buildVoiceClient(config: AppConfig): VoiceClient {
  return new VoiceBridgeProcessClient({
    pythonBin: config.voicePythonBin,
    bridgeScriptPath: config.voiceBridgeScriptPath,
    sttModel: config.sttModel,
    sttLanguage: config.sttLanguage,
    sttDevice: config.sttDevice,
    sttComputeType: config.sttComputeType,
    sttStartTimeoutMs: config.sttStartTimeoutMs,
    sttSilenceMs: config.sttSilenceMs,
    sttMaxUtteranceMs: config.sttMaxUtteranceMs,
    sttVadMode: config.sttVadMode,
    sttPrerollMs: config.sttPrerollMs,
    audioInputDevice: config.audioInputDevice,
    audioOutputDevice: config.audioOutputDevice,
    ttsModelPath: config.ttsModelPath,
    ttsSpeaker: config.ttsSpeaker,
    ttsLengthScale: config.ttsLengthScale,
    ttsNoiseScale: config.ttsNoiseScale,
    ttsNoiseWScale: config.ttsNoiseWScale,
    ttsVolume: config.ttsVolume,
  });
}

export async function runVoiceCli(input: {
  runtime?: CliRuntime;
  voiceClient?: VoiceClient;
  feedback?: ProcessingFeedback;
} = {}): Promise<void> {
  const runtime = input.runtime ?? createCliRuntime();
  const voiceClient = input.voiceClient ?? buildVoiceClient(runtime.config);
  const feedback = input.feedback ?? createProcessingFeedback();

  console.log("lbot> Cerebro online em modo voz. Diga 'sair' para encerrar.");

  try {
    while (true) {
      const heard = await voiceClient.listenOnce();

      if (heard.timedOut) {
        continue;
      }

      const userText = heard.transcript.trim();

      if (!userText) {
        if (heard.heardSpeech) {
          console.log("voce> [nao entendi]");
        }

        continue;
      }

      console.log(`voce> ${userText}`);

      if (isExitCommand(userText)) {
        break;
      }

      try {
        const prepared = await prepareCliTurn({
          userText,
          session: runtime.session,
          planner: runtime.planner,
          executor: runtime.executor,
        });

        for (const line of prepared.initialConsoleLines) {
          console.log(line);
        }

        await voiceClient.speak(prepared.initialSpokenText);

        let completed;

        if (prepared.plan.toolCall) {
          const stopFeedback = feedback.start(prepared.progressMessage ?? "processando...");

          try {
            completed = await completeCliTurn({
              plan: prepared.plan,
              session: runtime.session,
              executor: runtime.executor,
            });
          } finally {
            stopFeedback();
          }
        } else {
          completed = await completeCliTurn({
            plan: prepared.plan,
            session: runtime.session,
            executor: runtime.executor,
          });
        }

        for (const line of completed.toolConsoleLines) {
          console.log(line);
        }

        if (completed.toolSpokenText) {
          await voiceClient.speak(completed.toolSpokenText);
        }
      } catch (error) {
        console.log(formatPlannerError(error));
        await voiceClient.speak(spokenPlannerError());
      }
    }
  } finally {
    try {
      await voiceClient.dispose?.();
    } finally {
      await runtime.dispose();
    }
  }
}

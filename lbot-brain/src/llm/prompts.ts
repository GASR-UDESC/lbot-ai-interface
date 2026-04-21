import type { SessionEvent } from "../core/types";
import type { LlmMessage } from "./lm-studio-client";

function renderEvent(event: SessionEvent): string {
  switch (event.type) {
    case "user_message":
      return `[user] ${event.text}`;
    case "turn_plan":
      return `[assistant] kind=${event.plan.kind} text=${JSON.stringify(event.plan.assistantText)} tool=${event.plan.toolCall?.tool ?? "none"}`;
    case "tool_result":
      return `[tool_result] tool=${event.result.tool} ok=${event.result.ok} summary=${JSON.stringify(event.result.summary)} errorCode=${event.result.errorCode ?? "none"}`;
  }
}

function renderSessionContext(sessionEvents: readonly SessionEvent[]): string {
  if (sessionEvents.length === 0) {
    return "Nenhum contexto anterior.";
  }

  return sessionEvents.slice(-20).map(renderEvent).join("\n");
}

export function buildPlannerMessages(input: {
  userText: string;
  sessionEvents: readonly SessionEvent[];
}): LlmMessage[] {
  const { userText, sessionEvents } = input;

  const systemPrompt = [
    "Voce e o lbot, o cerebro conversacional de um robo.",
    "Sua personalidade e brincalhona, leve e simpatica, mas voce continua objetivo.",
    "Voce responde em portugues do Brasil, a menos que o usuario use outro idioma.",
    "Seu trabalho e devolver um plano tipado para o runtime, nao texto livre.",
    "Retorne somente JSON cru. Nao use markdown, nao use bloco de codigo, nao explique nada fora do JSON.",
    "O JSON sempre deve ter estas chaves: kind, assistantText, toolCall.",
    "O campo kind deve ser exatamente um destes valores: chat, tool, clarify, refuse.",
    "Se kind for chat, clarify ou refuse, toolCall deve ser null.",
    "Se kind for tool, toolCall deve ser um objeto valido.",
    "Quando houver toolCall, use exatamente um destes tools:",
    '- robot.execute para comandos fisicos, navegacao, movimento, acoes no mundo real.',
    '- vision.describe para pedidos de observacao, foto, descricao do que o robo esta vendo.',
    "Se houver toolCall, assistantText deve ser um preambulo curto e brincalhao, sem prometer sucesso.",
    'Exemplo bom: "Claro, vou tentar isso agora."',
    'Exemplo ruim: "Pronto, ja fiz."',
    'Exemplo de chat: {"kind":"chat","assistantText":"Oi, piloto. Como posso ajudar?","toolCall":null}',
    'Exemplo de tool fisica: {"kind":"tool","assistantText":"Claro, vou tentar isso agora.","toolCall":{"tool":"robot.execute","input":{"utteranceRaw":"anda 30 cm pra frente"}}}',
    'Exemplo de tool de visao: {"kind":"tool","assistantText":"Ja vou dar uma espiada.","toolCall":{"tool":"vision.describe","input":{"utteranceRaw":"o que voce esta vendo?"}}}',
    "Se a intencao for claramente fisica, use robot.execute mesmo quando o comando for ambiguo.",
    "Se a intencao for claramente sobre ver ou descrever uma cena, use vision.describe.",
    "Saudacoes simples, papo casual e perguntas sem acao fisica devem virar chat.",
    "Nao peca confirmacao para movimentos. O robo executa imediatamente.",
    "Se a duvida estiver entre tool e clarify para uma acao fisica ou de visao, prefira tool.",
    "Se for so conversa, responda com kind=chat e toolCall=null.",
    "Use kind=clarify apenas quando realmente faltar informacao indispensavel e a intencao nao estiver clara.",
    "Se precisar recusar, use kind=refuse.",
    "Nunca decomponha comandos do robo em varias etapas.",
    "Nunca altere o texto bruto do usuario dentro do toolCall.",
  ].join("\n");

  const sessionContext = renderSessionContext(sessionEvents);
  const userPrompt = [
    "Contexto recente da sessao:",
    sessionContext,
    "",
    "Mensagem atual do usuario:",
    userText,
    "",
    "Retorne somente o JSON do plano.",
  ].join("\n");

  return [
    {
      role: "system",
      content: systemPrompt,
    },
    {
      role: "user",
      content: userPrompt,
    },
  ];
}

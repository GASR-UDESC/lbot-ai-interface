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
    "Voce é o LBOT, um robô E-Puck inteligente desenvolvido pelo laboratório de robótica da UDESC (Universidade do Estado de Santa Catarina).",
    "Sua missão é ajudar usuários a controlar o robô, responder perguntas e interagir de forma eficiente, representando inovação, pesquisa e ensino em robótica e inteligência artificial.",
    "Voce é o cérebro conversacional do robô.",
    "Sua personalidade é cordial, educada e objetiva, sem exageros ou brincadeiras forçadas.",
    "Você responde em português do Brasil, a menos que o usuário use outro idioma.",
    "Seu trabalho é devolver um plano tipado para o runtime, não texto livre.",
    "Retorne somente JSON cru. Não use markdown, não use bloco de código, não explique nada fora do JSON.",
    "O JSON sempre deve ter estas chaves: kind, assistantText, toolCall.",
    "O campo kind deve ser exatamente um destes valores: chat, tool, clarify, refuse.",
    "Se kind for chat, clarify ou refuse, toolCall deve ser null.",
    "Se kind for tool, toolCall deve ser um objeto válido.",
    "Quando houver toolCall, use exatamente um destes tools:",
    '- robot.execute para comandos físicos, navegação, movimento, ações no mundo real.',
    '- vision.describe para pedidos de observação, descrição, análise visual, busca por objetos e perguntas sobre o que a câmera mostra.',
    "Se houver toolCall, assistantText deve ser um preâmbulo curto, cordial e neutro, sem prometer sucesso.",
    'Exemplo bom: "Certo, executando agora."',
    'Exemplo ruim: "Pronto, já fiz."',
    'Exemplo de chat: {"kind":"chat","assistantText":"Oi, humano. Como posso ajudar?","toolCall":null}',
    'Exemplo de tool física: {"kind":"tool","assistantText":"Certo, executando agora.","toolCall":{"tool":"robot.execute","input":{"utteranceRaw":"anda 30 cm pra frente"}}}',
    'Exemplo de tool de visão: {"kind":"tool","assistantText":"Vou analisar a imagem.","toolCall":{"tool":"vision.describe","input":{"utteranceRaw":"o que voce esta vendo?"}}}',
    "Se a intenção for claramente física, use robot.execute mesmo quando o comando for ambíguo.",
    "Se a intenção for claramente sobre ver, procurar, contar, descrever ou analisar algo visível, use vision.describe.",
    "Saudações simples, papo casual e perguntas sem ação física devem virar chat.",
    "Não peça confirmação para movimentos. O robô executa imediatamente.",
    "Se a dúvida estiver entre tool e clarify para uma ação física ou de visão, prefira tool.",
    "Se for só conversa, responda com kind=chat e toolCall=null.",
    "Use kind=clarify apenas quando realmente faltar informação indispensável e a intenção não estiver clara.",
    "Se precisar recusar, use kind=refuse.",
    "Nunca decomponha comandos do robô em várias etapas.",
    "Nunca altere o texto bruto do usuário dentro do toolCall.",
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

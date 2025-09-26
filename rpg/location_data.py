LOCATIONS = {
    # --- LOCAIS PRINCIPAIS (acessíveis via .explorar) ---
    "floresta": {
        "nome_exibicao": "Floresta Sombria",
        "eventos": [
            {
                "type": "combat",
                "description": "Um vulto se move entre os arbustos... um Goblin emboscador salta com sua adaga enferrujada!",
                "weight": 60,
                "data": {"monsters": ["Goblin Emboscador", "Goblin Recruta"]}
            },
            {
                "type": "loot",
                "description": "Você encontra o tronco oco de uma árvore, dentro há moedas antigas e uma erva medicinal.",
                "weight": 25,
                "data": {"items": [{"nome": "Erva de Cura", "quantidade": 1}], "gold": 20}
            },
            {
                "type": "choice",
                "description": "Um corvo pousa em um galho e olha fixamente para você. À frente, há dois caminhos misteriosos.",
                "weight": 70,
                "data": {
                    "prompt": "Seguir o corvo ou confiar no instinto?",
                    "options": {
                        "cabana_floresta": "Seguir o corvo até a cabana 🏠",
                        "trilha_escura": "Confiar no instinto e adentrar a trilha escura 🌲"
                    }
                }
            }
        ]
    },

    "caverna": {
        "nome_exibicao": "Caverna Ecoante",
        "eventos": [
            {
                "type": "combat",
                "description": "Do teto caem pedras, revelando um Morcego Gigante faminto!",
                "weight": 65,
                "data": {"monsters": ["Morcego Gigante", "Troll da Caverna"]}
            },
            {
                "type": "loot",
                "description": "Entre fendas úmidas, você encontra um baú enferrujado contendo pedras preciosas.",
                "weight": 25,
                "data": {"items": [{"nome": "Cristal Luminoso", "quantidade": 2}], "gold": 40}
            },
            {
                "type": "choice",
                "description": "Você encontra uma passagem bifurcada: uma trilha leva a um lago subterrâneo, outra a um túnel mais fundo e estreito.",
                "weight": 40,
                "data": {
                    "prompt": "Qual caminho você escolhe?",
                    "options": {
                        "lago_subterraneo": "Explorar o Lago Subterrâneo 💧",
                        "tunel_profundo": "Seguir pelo túnel escuro ⛏️"
                    }
                }
            }
        ]
    },

    # --- SUB-LOCAIS (acessíveis apenas via escolhas) ---
    "cabana_floresta": {
        "nome_exibicao": "Cabana na Floresta",
        "eventos": [
            {
                "type": "loot",
                "description": "Sobre a lareira apagada, há um saco de moedas e um frasco de líquido azul.",
                "weight": 50,
                "data": {"items": [{"nome": "Poção de Mana Fraca", "quantidade": 1}], "gold": 30}
            },
            {
                "type": "combat",
                "description": "As velas se acendem sozinhas... um Espírito Ancestral ergue-se contra você!",
                "weight": 30,
                "data": {"monsters": ["Espírito Ancestral"]}
            },
            {
                "type": "choice",
                "description": "No canto da cabana, você encontra um alçapão no chão coberto por tapete.",
                "weight": 20,
                "data": {
                    "prompt": "Abrir o alçapão ou ignorá-lo?",
                    "options": {
                        "porao_cabana": "Abrir e descer ao porão escuro 🔦",
                        "floresta": "Ignorar e voltar para a floresta 🌲"
                    }
                }
            }
        ]
    },

    "pantano": {
        "nome_exibicao": "Pântano Enevoado",
        "eventos": [
            {
                "type": "combat",
                "description": "A água turva borbulha... uma Serpente do Brejo surge do lodo!",
                "weight": 70,
                "data": {"monsters": ["Serpente do Brejo"]}
            },
            {
                "type": "combat",
                "description": "O nevoeiro se agita e várias sombras emergem: uma Hidra Jovem se ergue diante de você!",
                "weight": 30,
                "data": {"monsters": ["Hidra Jovem"]}
            },
            {
                "type": "loot",
                "description": "Você encontra ossos parcialmente enterrados com um medalhão de prata.",
                "weight": 25,
                "data": {"items": [{"nome": "Medalhão Antigo", "quantidade": 1}], "gold": 15}
            }
        ]
    },

    "trilha_escura": {
        "nome_exibicao": "Trilha Escura",
        "eventos": [
            {
                "type": "combat",
                "description": "As árvores se fecham ao redor e uma matilha faminta de lobos te encara!",
                "weight": 80,
                "data": {"monsters": ["Lobo Cinzento", "Lobo Alfa"]}
            },
            {
                "type": "choice",
                "description": "Um vulto encapuzado aparece na estrada. Ele faz sinal para você se aproximar.",
                "weight": 40,
                "data": {
                    "prompt": "Você confia nele?",
                    "options": {
                        "mercador_sombrio": "Se aproximar do estranho 🕯️",
                        "floresta": "Ignorar e voltar para a floresta 🌲"
                    }
                }
            }
        ]
    },

    # --- NOVOS SUB-LOCAIS ---
    "lago_subterraneo": {
        "nome_exibicao": "Lago Subterrâneo",
        "eventos": [
            {
                "type": "combat",
                "description": "Das águas geladas surge uma Serpente Aquática!",
                "weight": 50,
                "data": {"monsters": ["Serpente Aquática"]}
            },
            {
                "type": "loot",
                "description": "No fundo do lago, você encontra uma caixa encharcada contendo moedas e uma pérola.",
                "weight": 40,
                "data": {"items": [{"nome": "Pérola Brilhante", "quantidade": 1}], "gold": 60}
            },
            {
                "type": "choice",
                "description": "Você vê uma pequena ilha no meio do lago. Parece haver algo lá.",
                "weight": 30,
                "data": {
                    "prompt": "Nadar até a ilha ou voltar?",
                    "options": {
                        "ilha_lago": "Nadar até a ilha 🏝️",
                        "caverna": "Retornar para a caverna ⛰️"
                    }
                }
            }
        ]
    },

    "tunel_profundo": {
        "nome_exibicao": "Túnel Profundo",
        "eventos": [
            {
                "type": "combat",
                "description": "Um rugido ecoa... um Golem de Pedra desperta bloqueando o caminho!",
                "weight": 70,
                "data": {"monsters": ["Golem de Pedra"]}
            },
            {
                "type": "loot",
                "description": "Você encontra runas antigas gravadas, uma delas parece carregada de energia mágica.",
                "weight": 30,
                "data": {"items": [{"nome": "Runa Brilhante", "quantidade": 1}], "gold": 25}
            }
        ]
    },

    "porao_cabana": {
        "nome_exibicao": "Porão da Cabana",
        "eventos": [
            {
                "type": "combat",
                "description": "Ratos monstruosos saem das sombras, rangendo os dentes!",
                "weight": 60,
                "data": {"monsters": ["Rato Gigante", "Rato Gigante"]}
            },
            {
                "type": "loot",
                "description": "Entre caixas podres, você encontra vinho envelhecido e algumas moedas.",
                "weight": 40,
                "data": {"items": [{"nome": "Vinho Antigo", "quantidade": 1}], "gold": 10}
            }
        ]
    },

    "mercador_sombrio": {
        "nome_exibicao": "Mercador Sombrio",
        "eventos": [
            {
                "type": "loot",
                "description": "O mercador encapuzado abre sua sacola e oferece itens raros em troca de algumas moedas.",
                "weight": 100,
                "data": {
                    "items": [
                        {"nome": "Poção Misteriosa", "quantidade": 1},
                        {"nome": "Adaga Enfeitiçada", "quantidade": 1}
                    ],
                    "gold": -30  # custo de compra, se tu for implementar sistema de troca
                }
            }
        ]
    },

    "ilha_lago": {
        "nome_exibicao": "Ilha do Lago",
        "eventos": [
            {
                "type": "loot",
                "description": "Na areia úmida da ilha você encontra um baú com joias reluzentes.",
                "weight": 60,
                "data": {"items": [{"nome": "Anel de Safira", "quantidade": 1}], "gold": 100}
            },
            {
                "type": "combat",
                "description": "Um elemental da água ergue-se do lago, furioso pela sua presença!",
                "weight": 40,
                "data": {"monsters": ["Elemental da Água"]}
            }
        ]
    }
}

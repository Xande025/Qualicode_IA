from final_ipo_agent_improved import FinalIPOAgentImproved

agent = FinalIPOAgentImproved()

question_data = [
"Segurança","mais segurança","segurança nas ruas","policiamento","botou mais polícia","polisia","segurança pública","policiamento melhor",
"Transporte","transporte público","ônibus","mais ônibus","onibus melhor","transporte","coletivos melhores","mais linhas de ônibus","linhas de onibus",
"Saúde","hospital","hospitais melhores","mais médicos","médico","médicos no posto","posto de saúde","posto saúde","posto medico","atendimento médico","atendimento no hospital",
"Infraestrutura","calçamento","calçamento de ruas","rua calçada","arrumou as ruas","asfaltou","asfaltmento","asfalto","arrumou buracos","tapou os buracos",
"Educação","escola","escolas boas","ensino melhor","educação de qualidade","mais escolas","mais professores","professores bons","estudo melhor","estudar",
"Egotos","Saneamento basico","Esgoto","Esgotos emtupidos"
]

f17_list = [
"1 | Saúde",
"2 | Pavimentação/asfalto",
"3 | Educação",
"4 | Melhorias nos bairros",
"5 | Segurança/policiamento"
]

res = agent.process_single_question_with_chatgpt(question_data, {"Saúde":1, "Pavimentação/asfalto":2, "Educação":3, "Melhorias nos bairros":4, "Segurança/policiamento":5}, 'TESTE')
print('=== CODES ===')
print(res['final_codes'])
print('\n=== GROUPS (sample) ===')
for k,v in list(res['groups'].items())[:30]:
    print(k,':',v)

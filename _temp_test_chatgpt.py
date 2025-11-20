from final_ipo_agent_improved import FinalIPOAgentImproved
agent = FinalIPOAgentImproved()
question_data = ['Melhorou a saude','saude','foi bomn para saúde','arrumou os barrios','barios','ajuda o povo','ajuda as pessoas','esgotos','saneamento básico','saneamento basico','esgoto','esgoto','esgotos','esgot','esgoto','esgotos','saneamento basico, esgoto','pavimentação de ruas','pavimentonas ruas','ruas melhores','rua','educação','molhor educacao','escolas melhores']
existing_codes = {'Saúde': 1, 'Pavimentação/asfalto': 2, 'Educação': 3, 'Melhorias nos bairros': 4}
res = agent.process_single_question_with_chatgpt(question_data, existing_codes, '16 - TESTE')
print('\n--- RESULTADO ---')
for k,v in res.items():
    if k in ('final_codes','groups'):
        print(k,':',v)
    else:
        print(k,':',type(v))

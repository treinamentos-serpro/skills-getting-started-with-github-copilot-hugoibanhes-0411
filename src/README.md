# API de Atividades da Mergington High School

Uma aplicação FastAPI super simples que permite que estudantes visualizem e se inscrevam em atividades extracurriculares.

## Funcionalidades

- Visualizar todas as atividades extracurriculares disponíveis
- Inscrever-se em atividades

## Primeiros Passos

1. Instale as dependências:

   ```
   pip install fastapi uvicorn
   ```

2. Execute a aplicação:

   ```
   python app.py
   ```

3. Abra seu navegador e acesse:
   - Documentação da API: http://localhost:8000/docs
   - Documentação alternativa: http://localhost:8000/redoc

## Endpoints da API

| Método | Endpoint                                                          | Descrição                                                                   |
| ------ | ----------------------------------------------------------------- | --------------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Obtém todas as atividades com seus detalhes e contagem atual de participantes |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Inscreve-se em uma atividade                                                |

Para cancelar uma inscrição, envie `DELETE /activities/{activity_name}/unregister?email=student@mergington.edu`.
A operação remove apenas a inscrição na atividade indicada e retorna HTTP 404 se a atividade ou o participante não existir.

## Modelo de Dados

A aplicação usa um modelo de dados simples com identificadores significativos:

1. **Activities** - Usa o nome da atividade como identificador:

   - Descrição
   - Horário
   - Número máximo de participantes permitidos
   - Lista de emails dos estudantes inscritos

2. **Students** - Usa email como identificador:
   - Nome
   - Série/Ano escolar

Todos os dados são armazenados em memória, o que significa que os dados serão resetados quando o servidor reiniciar.

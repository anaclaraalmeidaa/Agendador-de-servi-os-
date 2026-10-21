# Agendador

Site simples de agendamento para autônomos e pequenos negócios. O profissional cadastra serviços e horários de atendimento; clientes escolhem um horário livre sem criar conta.

## Requisitos

- Docker Desktop ou Docker Engine com Compose v2.

## Instalação e uso

1. Copie `.env.example` para `.env` e troque `POSTGRES_PASSWORD` e `SESSION_SECRET` por valores aleatórios. O exemplo é somente para desenvolvimento local.
2. Inicie o site com `docker compose up` (Compose constrói a imagem na primeira execução).
3. Em outro terminal, crie a conta do profissional: `docker compose exec web python scripts/create_professional.py`. Informe nome, e-mail, slug do link, telefone com DDI e senha forte. A senha é armazenada com scrypt; não é salva em texto simples.
4. Abra `http://localhost:8000/login` para entrar. Cadastre serviços e horários semanais, e compartilhe o link `/p/seu-slug`.
5. Para parar o site, use Ctrl+C. Os dados ficam no volume `postgres_data`.

## Testes

Os testes usam um PostgreSQL separado, nunca SQLite. Execute `docker compose --profile test run --rm tests`; o serviço `test-db` fica isolado do banco de desenvolvimento.

Os testes de agendamento validam disponibilidade e conflitos. A proteção definitiva contra sobreposição é a constraint PostgreSQL `appointments_no_overlap`, uma exclusão GiST sobre intervalos `[início, fim)` por profissional. Ela permite horários adjacentes, bloqueia sobreposição inclusive em transações concorrentes e deixa horários disponíveis após cancelamento.

## Configuração e segurança

As variáveis de ambiente são documentadas em `.env.example`. `.env` e arquivos locais de credenciais estão excluídos do Git. Nunca publique senhas ou chaves no repositório. O login do profissional exige sessão assinada e os formulários de alteração validam token CSRF. Em produção HTTPS, configure `SESSION_COOKIE_SECURE=true`. A página pública só pede nome e telefone ao cliente.

## Funcionalidades

- Cadastro/edição de serviços e períodos semanais.
- Link público com disponibilidade e confirmação de agendamento.
- Agenda diária do profissional e cancelamento com pelo menos duas horas de antecedência.
- Botão de WhatsApp com mensagem pronta iniciada pelo cliente.
- Páginas responsivas e mensagens em português.

Pagamentos, envio automático de mensagens e aplicativo nativo não fazem parte deste projeto.

## HTMX

A interface usa HTMX 2.0.4, distribuído localmente em `app/static/js/htmx.min.js` sob licença Zero-Clause BSD (0BSD). Os formulários HTML também funcionam sem JavaScript.

# Feature Specification: Agendamento Online

**Feature Branch**: `001-agendamento-online`

**Created**: 2026-10-19

**Status**: Draft

**Input**: User description: "Um site de agendamento de horários para autônomos e pequenos negócios. O profissional cadastra serviços e horários de atendimento, acompanha a agenda, cancela agendamentos e compartilha um link. O cliente escolhe um serviço e horário livre, informa nome e telefone, confirma sem conta e pode abrir o WhatsApp com uma mensagem pronta. Não são permitidos conflitos de horário nem reservas no passado ou fora do atendimento. Pagamentos, mensagens automáticas e aplicativo de celular estão fora do escopo."
## Clarifications

### Session 2026-10-19
- Q: Uma conta e um link público devem atender um único profissional, ou uma empresa pode cadastrar vários profissionais com agendas separadas? → A: Uma conta e um link público atendem um único profissional.
- Q: Com que intervalo o site deve oferecer horários de início para cada serviço? → A: O intervalo entre inícios é igual à duração do serviço, começando no início de cada período de atendimento.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publicar serviços e horários (Priority: P1)

Como profissional, quero cadastrar meus serviços e definir meus dias e horários de atendimento para que clientes vejam opções corretas ao agendar.

**Why this priority**: A disponibilidade e os serviços são pré-requisitos para qualquer reserva.

**Independent Test**: Um profissional configura um serviço com duração e uma grade semanal e confirma que a página pública exibe o serviço e somente horários compatíveis com a grade.

**Acceptance Scenarios**:

1. **Given** um profissional autenticado, **When** cadastra um serviço com nome e duração válida, **Then** o serviço fica disponível na sua página de agendamento.
2. **Given** um profissional autenticado, **When** define dias e horários de atendimento, **Then** a disponibilidade pública respeita esses períodos.
3. **Given** o profissional possui serviços publicados, **When** solicita seu link público, **Then** pode copiar esse link para compartilhá-lo em redes sociais e aplicativos de conversa.

---

### User Story 2 - Reservar um horário disponível (Priority: P1)

Como cliente, quero escolher um serviço e um horário livre e informar meu nome e telefone para confirmar sem criar uma conta.

**Why this priority**: A reserva direta é o principal valor oferecido pelo site ao cliente e ao profissional.

**Independent Test**: Um cliente abre o link público, escolhe um serviço, seleciona horário futuro disponível, informa nome e telefone e recebe a confirmação.

**Acceptance Scenarios**:

1. **Given** uma página pública com serviços e disponibilidade, **When** o cliente escolhe um serviço, **Then** vê somente horários futuros dentro do atendimento que comportam a duração do serviço.
2. **Given** um horário livre, **When** o cliente informa nome e telefone e confirma, **Then** o agendamento é criado e associado ao serviço, profissional e horário escolhidos.
3. **Given** dois clientes tentam confirmar horários que se sobrepõem para o mesmo profissional, **When** as confirmações são processadas, **Then** no máximo uma é aceita e a outra recebe uma mensagem clara em português para escolher outro horário.
4. **Given** um cliente sem conta, **When** informa apenas nome e telefone e confirma, **Then** consegue concluir a reserva sem cadastro ou autenticação.
5. **Given** um horário no passado ou fora do atendimento, **When** o cliente tenta reservá-lo, **Then** o sistema recusa a reserva e informa o motivo em português.

---

### User Story 3 - Consultar e cancelar agendamentos (Priority: P2)

Como profissional, quero consultar a agenda do dia e cancelar uma reserva para manter minha rotina atualizada e liberar o horário.

**Why this priority**: A agenda e o cancelamento permitem que o profissional administre reservas existentes.

**Independent Test**: O profissional autenticado abre a agenda de um dia, identifica uma reserva e a cancela; a reserva deixa de ocupar o horário.

**Acceptance Scenarios**:

1. **Given** um profissional com reservas, **When** abre a agenda de uma data, **Then** vê os agendamentos daquele dia com serviço, horário e dados de contato do cliente.
2. **Given** uma reserva ativa cujo início está a mais de 2 horas, **When** o profissional a cancela, **Then** ela deixa de ocupar o horário e esse horário volta a aparecer como disponível se ainda estiver no futuro e dentro do atendimento.
3. **Given** uma reserva ativa cujo início está a menos de 2 horas, **When** o profissional tenta cancelá-la, **Then** o cancelamento é recusado, a reserva permanece ativa e o sistema informa o prazo mínimo em português.
4. **Given** uma reserva ativa cujo início está exatamente a 2 horas, **When** o profissional a cancela, **Then** o cancelamento é permitido.
5. **Given** um profissional, **When** consulta ou tenta cancelar reservas, **Then** só pode acessar e alterar reservas associadas à própria conta.

---

### User Story 4 - Abrir conversa no WhatsApp após confirmar (Priority: P2)

Como cliente, quero abrir o WhatsApp com uma mensagem de confirmação pronta para entrar em contato com o profissional se necessário.

**Why this priority**: A ação facilita o contato depois da reserva sem exigir envio automático pelo sistema.

**Independent Test**: Depois de confirmar uma reserva, o cliente aciona o botão de WhatsApp e o aplicativo ou site do WhatsApp abre com o contato do profissional e uma mensagem preenchida com os dados essenciais da reserva.

**Acceptance Scenarios**:

1. **Given** uma reserva confirmada e um contato de WhatsApp cadastrado pelo profissional, **When** o cliente aciona o botão de WhatsApp, **Then** abre-se o WhatsApp com uma mensagem pronta contendo serviço, data e horário.
2. **Given** o cliente não tem o WhatsApp instalado, **When** aciona o botão, **Then** pode continuar pelo WhatsApp na web ou recebe uma orientação clara.

### Edge Cases

- Dois pedidos simultâneos para o mesmo profissional cujos períodos se cruzam: apenas um pode ser confirmado.
- Um serviço cuja duração ultrapassa o fim do período de atendimento não deve gerar horários oferecidos.
- Um horário que acabou de ser reservado ou cancelado deve ter sua disponibilidade atualizada para novas consultas.
- Uma reserva cancelada não ocupa mais o horário; uma reserva concluída ou ativa continua ocupando seu período. O profissional pode cancelar uma reserva ativa quando faltarem exatamente 2 horas ou mais, mas não pode cancelá-la com menos de 2 horas para o início.
- Datas e horários devem ser apresentados no fuso local do profissional; mudanças de horário local devem manter uma única interpretação para cada reserva.
- Nome ou telefone ausente ou inválido impede a confirmação e apresenta instrução em português.
- Falha ao abrir o WhatsApp não desfaz a reserva já confirmada.
- Um link público inválido ou de profissional sem serviços e horários configurados apresenta orientação compreensível, sem expor dados privados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema MUST permitir que um único profissional entre em uma área autenticada para administrar os próprios serviços, horários e agendamentos associados à sua conta e ao seu link público.
- **FR-002**: O sistema MUST permitir cadastrar e editar serviços com nome e duração.
- **FR-003**: O sistema MUST permitir definir os dias e períodos de atendimento do profissional.
- **FR-004**: O sistema MUST fornecer ao profissional um link público estável para divulgar sua página de agendamento.
- **FR-005**: O sistema MUST apresentar ao cliente os serviços disponíveis e os horários livres compatíveis com o serviço escolhido.
- **FR-020**: Para cada período de atendimento, o sistema MUST oferecer inícios de horário em intervalos iguais à duração do serviço escolhido, a partir do início desse período.
- **FR-006**: O sistema MUST exigir nome e telefone do cliente para confirmar uma reserva e MUST NOT exigir conta do cliente.
- **FR-007**: O sistema MUST criar a reserva somente após validar novamente a disponibilidade no momento da confirmação.
- **FR-008**: O sistema MUST impedir que períodos de agendamentos ativos se sobreponham para o mesmo profissional, inclusive em confirmações simultâneas. Horários adjacentes são permitidos quando um termina exatamente quando o próximo começa.
- **FR-009**: O sistema MUST recusar reservas com início no passado ou cujo período não esteja integralmente dentro do horário de atendimento definido.
- **FR-010**: O sistema MUST exibir ao profissional sua agenda por dia, incluindo serviço, horário e nome e telefone do cliente.
- **FR-011**: O sistema MUST permitir que o profissional cancele apenas agendamentos associados à própria conta e MUST permitir o cancelamento somente quando faltarem pelo menos 2 horas para o início. Cancelamentos permitidos MUST liberar o período para novas reservas válidas; tentativas após o limite MUST ser recusadas com mensagem clara em português.
- **FR-012**: Após confirmar uma reserva, o sistema MUST mostrar um botão que abre o WhatsApp com mensagem pronta contendo serviço, data e horário, direcionada ao contato de WhatsApp informado pelo profissional.
- **FR-013**: O sistema MUST NOT enviar mensagens automaticamente; o cliente inicia o contato ao usar o botão do WhatsApp.
- **FR-014**: O site MUST apresentar controles e mensagens de agendamento em português e MUST permitir completar os fluxos em telas de celular.
- **FR-015**: O sistema MUST fornecer mensagens claras em português quando uma reserva for recusada, cancelada ou não puder ser concluída.
- **FR-016**: O sistema MUST incluir testes automáticos para os fluxos principais, com cobertura explícita de horários repetidos, sobreposição de duração, datas passadas e períodos fora do atendimento.
- **FR-017**: O projeto MUST incluir um README com instruções de instalação, configuração e uso.
- **FR-018**: Senhas, chaves e outros segredos MUST NOT ser enviados ou versionados no GitHub.
- **FR-019**: O produto MUST NOT incluir pagamentos, envio automático de mensagens ou aplicativo nativo de celular nesta entrega.

### Key Entities *(include if feature involves data)*

- **Profissional**: Pessoa ou negócio que oferece serviços; possui dados de acesso, contato de WhatsApp, fuso horário, horários de atendimento e link público.
- **Serviço**: Oferta do profissional, identificada por nome e duração.
- **Horário de atendimento**: Dia da semana e período em que o profissional aceita reservas.
- **Agendamento**: Reserva de um serviço por um cliente, com profissional, início e fim, nome e telefone do cliente e estado ativo ou cancelado.
- **Cliente**: Pessoa que reserva sem criar conta; fornece nome e telefone para a reserva.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em testes de confirmação simultânea para períodos sobrepostos do mesmo profissional, exatamente uma reserva é confirmada e nenhuma sobreposição permanece ativa.
- **SC-002**: Em testes de validação, 100% das tentativas de reservar no passado ou fora do período de atendimento são recusadas.
- **SC-003**: Um profissional consegue cadastrar um serviço, configurar atendimento e copiar o link público em até 5 minutos, sem ajuda externa.
- **SC-004**: Pelo menos 90% dos participantes de uma avaliação conseguem concluir uma reserva em celular sem ajuda e em até 2 minutos.
- **SC-005**: Em testes de usabilidade, pelo menos 90% dos clientes identificam corretamente se a reserva foi confirmada e como abrir o WhatsApp.
- **SC-006**: Após cancelar uma reserva, o horário volta a aparecer como livre em até 5 segundos, desde que ainda seja futuro e esteja dentro do atendimento.
- **SC-007**: Em todos os testes de cancelamento, 100% das tentativas feitas com pelo menos 2 horas de antecedência são permitidas e 100% das tentativas feitas com menos de 2 horas são recusadas.

## Assumptions

- Cada conta e link público representam um único profissional, que só pode administrar os próprios dados e agendamentos.
- A autenticação do profissional é necessária para proteger agenda e configurações; o cliente não tem conta.
- O profissional informa um número apto a receber conversas no WhatsApp para compor o destino do botão.
- A duração cadastrada define o período ocupado pela reserva; períodos que se cruzam contam como conflito, mesmo quando seus horários de início diferem.
- Os horários usam o fuso local configurado para o profissional. Os horários oferecidos começam no início de cada período de atendimento e avançam em intervalos iguais à duração do serviço selecionado.
- O botão do WhatsApp apenas prepara uma mensagem para envio voluntário pelo cliente; a confirmação do agendamento não depende de abrir ou enviar essa mensagem.
- O site deve funcionar em navegadores móveis e desktop; a entrega não inclui aplicativo nativo.
- Os critérios de usabilidade serão verificados em avaliação com participantes representativos antes da conclusão do produto.
- Na primeira versão, uma pessoa responsável provisiona a conta do profissional antes do primeiro acesso; não há cadastro público de profissionais.





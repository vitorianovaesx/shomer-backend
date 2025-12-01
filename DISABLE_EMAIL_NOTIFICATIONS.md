# Como Desabilitar Notificações de Email do GitHub Actions

Para parar de receber emails sobre falhas do CI/health check:

## Opção 1: Via Interface Web do GitHub (Recomendado)

1. Vá para o repositório no GitHub
2. Clique em **Settings** (Configurações)
3. No menu lateral, clique em **Notifications**
4. Role até a seção **Actions**
5. **Desmarque** a opção **Email**
6. Salve as alterações

## Opção 2: Via GitHub CLI

```bash
gh api repos/:owner/:repo --method PATCH \
  -f notifications_enabled=false
```

## Opção 3: Configuração de Repositório

1. Vá para **Settings** > **Notifications**
2. Em **Actions**, desmarque:
   - ✅ Email notifications for failed workflows
   - ✅ Email notifications for cancelled workflows

## Opção 4: Configuração Global da Conta

1. Vá para seu perfil GitHub
2. **Settings** > **Notifications**
3. Em **Actions**, desmarque as notificações de email

---

**Nota:** O workflow já está configurado para não enviar emails automaticamente, mas as configurações do GitHub podem sobrescrever isso.


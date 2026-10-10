# Correção do Meta Pixel — LP Kit Usucapião Pro

Projeto Lovable: **Pro Usucapião Kit** (https://lovable.dev/projects/304dffad-7f71-47ee-ba32-158feeeae6cb)
Domínio: usucapiao.allanportoarquiteto.com.br
Pixel usado nas campanhas: **1414869993251554**

**Problema:** a página não tem nenhum código do Meta Pixel. Por isso o Meta registrou
31 cliques e só 1 visualização da página de destino, e zero compras. As campanhas
ProRoi otimizam para "Compra" sem receber sinal nenhum.

---

## Opção A — colar no chat do Lovable (quando tiver créditos)

```
Instale o Meta Pixel nesta landing page. Hoje ela não tem nenhum pixel.
1. Pixel ID 1414869993251554: código base padrão (fbevents.js) no <head> via src/routes/__root.tsx,
   com fbq('init','1414869993251554') e fbq('track','PageView'), mais o fallback <noscript>.
   Precisa funcionar com o SSR do TanStack Start, sem quebrar a hidratação.
2. Em src/routes/index.tsx, disparar ViewContent uma vez ao carregar
   (content_name 'Kit Usucapião Pro', value 47, currency 'BRL').
3. Em TODOS os links para o CHECKOUT_URL da Hotmart, disparar InitiateCheckout no clique
   (value 47, BRL). Os links "#oferta" NÃO disparam.
4. Repassar utm_source, utm_medium, utm_campaign, utm_term, utm_content e fbclid da URL atual para o
   CHECKOUT_URL, mantendo o parâmetro bid.
5. Checar se window.fbq existe antes de chamar. Não mexer no layout nem nos textos.
```

## Opção B — editar o código você mesmo (modo Code do Lovable)

### 1) `src/routes/__root.tsx`: dentro de `head: () => ({ ... })`, junto de `meta` e `links`, acrescente:

```tsx
    scripts: [
      {
        children: `!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;
n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init','1414869993251554');fbq('track','PageView');`,
      },
    ],
```

E em `RootShell`, logo depois de `<body>`:

```tsx
        <noscript>
          <img height="1" width="1" style={{ display: "none" }} alt=""
            src="https://www.facebook.com/tr?id=1414869993251554&ev=PageView&noscript=1" />
        </noscript>
```

### 2) `src/routes/index.tsx`

Logo abaixo de `const OFFER_MINUTES = 20;`, adicione:

```tsx
declare global {
  interface Window { fbq?: (...args: unknown[]) => void }
}

const PIXEL_PRODUCT = { content_name: "Kit Usucapião Pro", value: 47, currency: "BRL" };

function track(event: string, params?: Record<string, unknown>) {
  if (typeof window !== "undefined" && typeof window.fbq === "function") window.fbq("track", event, params);
}

const PASS_PARAMS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid"];

function checkoutHref() {
  if (typeof window === "undefined") return CHECKOUT_URL;
  const target = new URL(CHECKOUT_URL);
  const current = new URLSearchParams(window.location.search);
  PASS_PARAMS.forEach((key) => {
    const value = current.get(key);
    if (value) target.searchParams.set(key, value);
  });
  return target.toString();
}

function CheckoutLink({ className, children }: { className: string; children: React.ReactNode }) {
  const [href, setHref] = useState(CHECKOUT_URL);
  useEffect(() => setHref(checkoutHref()), []);
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={className}
      onClick={() => track("InitiateCheckout", PIXEL_PRODUCT)}>
      {children}
    </a>
  );
}
```

Dentro de `function LandingPage() {`, antes do `return`:

```tsx
  useEffect(() => {
    track("ViewContent", { ...PIXEL_PRODUCT, content_category: "Templates" });
  }, []);
```

Troque os **3** links de checkout (`<a href={CHECKOUT_URL} target="_blank" rel="noopener noreferrer" className="...">...</a>`) por:

```tsx
<CheckoutLink className="btn">Quero baixar o kit agora</CheckoutLink>
<CheckoutLink className="btn">Quero o kit completo</CheckoutLink>
<CheckoutLink className="btn btn-neon"><span>QUERO BAIXAR AGORA</span><ArrowRight aria-hidden="true" /></CheckoutLink>
```

Depois clique em **Publish** no Lovable para a correção ir ao ar no domínio.

---

## 3) Compra (Purchase): configurar na Hotmart

A venda acontece no checkout da Hotmart, fora da sua LP. O evento de Compra só chega ao
Meta se o pixel também estiver cadastrado lá:

Hotmart → Produtos → Kit Usucapião Pro → **Ferramentas → Pixel de rastreamento** →
Facebook → ID **1414869993251554**. Marque o envio de "Iniciar checkout" e "Compra".
Se aparecer a opção de **API de Conversões**, ative também (ajuda com o bloqueio do iOS).

## 4) Como testar

1. Instale a extensão **Meta Pixel Helper** no Chrome e abra a LP: devem aparecer
   PageView e ViewContent com o ID 1414869993251554.
2. Clique em "Quero baixar o kit agora": deve aparecer InitiateCheckout.
3. No Gerenciador de Eventos → pixel → **Testar eventos**, confirme a chegada.

## 5) Pixel separado por produto (próximo passo)

Esta correção instala o **mesmo** pixel que as campanhas ProRoi já usam, para que elas
voltem a receber sinal agora mesmo. Para separar os públicos (arquitetos e engenheiros ×
lojistas), crie um pixel novo no Gerenciador de Eventos (ex.: "Pixel Kit Usucapião"),
troque o ID nos passos 1 e 3 e mude o pixel nos conjuntos das campanhas ProRoi.
Assim a Loja que Vende fica sozinha no pixel atual.

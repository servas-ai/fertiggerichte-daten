import{k as e}from"./UpTRTvzs.js";import{Ft as t,zi as n,zt as r}from"./SCEl3m1f.js";import{r as i}from"./Buhui6OR.js";import{n as a,t as o}from"./CGpJTda_.js";import{t as s}from"./e2DYYeyX.js";var c=new URL(`ALDISUEDVF_LatinWeb_02.VhpaPoj1.woff2`,import.meta.url).href;function l(e,t,n,r,i){return e?.length?u(e.join(`, `),t,n,r,i):``}function u(e,t,n,r,i){return`;(function (win, doc, style, timeout, consentCookieName, consentGroup, runOnUnknownConsent) {
  const STYLE_ID = 'at-body-style'

  function getParent() {
    return doc.getElementsByTagName('head')[0]
  }

  function addStyle(parent, id, def) {
    if (!parent) {
      return
    }

    const style = doc.createElement('style')
    style.id = id
    style.innerHTML = def
    parent.appendChild(style)
  }

  function removeStyle(parent, id) {
    if (!parent) {
      return
    }
    const style = doc.getElementById(id)
    if (!style) {
      return
    }
    parent.removeChild(style)
  }

  function getTargetConsent() {
    try {
      const consentCookie = document.cookie.split('; ').find(c => c.startsWith(consentCookieName + '='))
      if (!consentCookie) {
        return 'CONSENT_UNKNOWN'
      }
      const decodedCookie = new URLSearchParams(decodeURIComponent(consentCookie))
      const groups = decodedCookie.get('groups').split(',')
      const targetConsentGroup = groups.find(g => g.startsWith(consentGroup + ':'))
      if (!targetConsentGroup) {
        return 'CONSENT_UNKNOWN'
      }
      if (targetConsentGroup === consentGroup + ':1') {
        return 'CONSENT_YES'
      }
      if (targetConsentGroup === consentGroup + ':0') {
        return 'CONSENT_NO'
      }
      return 'CONSENT_UNKNOWN'
    } catch {
      return 'CONSENT_UNKNOWN'
    }
  }

  // run only if consent is given
  const targetConsent = getTargetConsent()
  if (targetConsent === 'CONSENT_NO') {
    return
  }
  if (targetConsent === 'CONSENT_UNKNOWN' && !runOnUnknownConsent) {
    return
  }

  addStyle(getParent(), STYLE_ID, style)
  setTimeout(function () {
    removeStyle(getParent(), STYLE_ID)
  }, timeout)
})(window, document, '${e} {opacity: 0 !important}', ${t}, '${n}', '${r}', ${i})
`}function d(e,t){for(let n of t.WEB_PRECONNECT_CORS_LINKS.split(`,`)||[])e.addPreconnectLink(n,``);for(let n of t.WEB_PRECONNECT_LINKS.split(`,`)||[])e.addPreconnectLink(n);for(let n of t.WEB_DNS_PREFETCH_LINKS.split(`,`)||[])e.addDnsPrefetchLink(n);return e}function f(e){return e.addFontPreloading(c)}function p(e,t,n){let r=t.WEB_LAUNCH_SCRIPT;return r?e.addScript(`webLaunch`,r,{async:!0}):(n.warn(`Source of WebLaunchScript is empty`),e)}function m(e,t,n){let r=l(n,t.ANTI_FLICKERING_SNIPPET_TIMEOUT_MS,t.TARGET_CONSENT_COOKIE,t.TARGET_CONSENT_GROUP,t.TARGET_RUN_ON_UNKNOWN_CONSENT);return e.addScriptString(`antiFlickeringSnippet`,r,{"data-anti-flickering-snippet":``})}var h=()=>{let c=e(),l=t(),u=r({seo:!1}),h=o(i.GENERAL,`useCommonHead`,c);function g(){let e=s.builder();if(f(e),d(e,c.$config.public),!l.isWebLaunchDisabled){let t=l.antiFlickeringSelectors;t&&t.length>0&&m(e,c.$config.public,t),p(e,c.$config.public,h)}return e.build()}a()||n(g),n({htmlAttrs:{lang:()=>u.value.htmlAttrs.lang}})};export{h as t};
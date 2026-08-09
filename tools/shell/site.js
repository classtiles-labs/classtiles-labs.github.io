
(function(){
  var bar=document.getElementById('bar');
  if(bar){addEventListener('scroll',function(){bar.classList.toggle('stuck',scrollY>8)},{passive:true});}

  // Einblenden beim Scrollen ist Kür. Der Inhalt ist per Default sichtbar; das Skript versteckt ihn
  // nur, um ihn danach einzublenden — und eine Sicherheitsleine macht ihn nach 1 s in JEDEM Fall
  // wieder sichtbar. Sonst könnte eine Umgebung, in der der IntersectionObserver nicht feuert,
  // die halbe Seite verschlucken.
  var els=document.querySelectorAll('.rev');
  if(els.length && !matchMedia('(prefers-reduced-motion: reduce)').matches
     && 'IntersectionObserver' in window){
    els.forEach(function(el){el.classList.add('pre')});
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.remove('pre');io.unobserve(e.target)}})},{threshold:.08});
    els.forEach(function(el){io.observe(el)});
    setTimeout(function(){els.forEach(function(el){el.classList.remove('pre')})},1000);
  }

  // Das Video wird erst geladen, wenn jemand auf Play tippt — bis dahin steht nur das Standbild.
  // Spart Ladezeit; kein YouTube-Embed, damit kein Fremd-Tracker lädt.
  var player=document.getElementById('player');
  if(!player) return;
  var started=false;
  function start(){
    if(started) return;
    started=true;
    var v=document.createElement('video');
    v.src=player.dataset.src; v.controls=true; v.autoplay=true; v.playsInline=true;
    var screen=player.querySelector('.screen');
    screen.innerHTML=''; screen.appendChild(v);
    v.scrollIntoView({block:'center'});
  }
  var o=document.getElementById('playoverlay'); if(o) o.addEventListener('click',start);
  var c=document.getElementById('playcta');     if(c) c.addEventListener('click',start);
})();

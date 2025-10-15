# _plugins/jekyll_player.rb
# Usage:
#   In your layout (once): {% jekyll_player_boot %}
#   Players anywhere:
#   {% jekyll_player /assets/audio/track.mp3,
#      game: Chrono Trigger, title: Battle with Magus, artist: Yasunori Mitsuda,
#      year: 1995, autoplay: false, loop: false, max_width: "720px" %}
#
# Notes:
# - Compact layout: no title bar / window controls.
# - Fills 100% width; optional max_width per instance.
# - First arg can be quoted or unquoted. Same-origin MP3s work best.

require "cgi"
require "digest"

module Jekyll
  module WinampHelpers
    def self.h(text) CGI.escapeHTML(text.to_s) end
    def self.unquote(s)
      s = s.to_s.strip
      s = s[1..-2] if (s.start_with?('"') && s.end_with?('"')) || (s.start_with?("'") && s.end_with?("'"))
      s
    end
    def self.parse_args(markup)
      raw = (markup || "").strip
      if raw.include?(",")
        first, rest = raw.split(",", 2)
      else
        first, rest = raw, ""
      end
      src_raw = (first || "").strip
      opts = {}
      rest.scan(/(\w+)\s*:\s*(".*?"|'.*?'|[^,]+)(?:,|$)/).each do |k, v|
        v = v.strip
        v = v[1..-2] if (v.start_with?('"') && v.end_with?('"')) || (v.start_with?("'") && v.end_with?("'"))
        opts[k.strip.downcase] = v
      end
      [src_raw, opts]
    end
  end

  # BOOT TAG: shared CSS + JS once
  class WinampPlayerBootTag < Liquid::Tag
    def render(_context)
      css = <<~CSS
        .jwamp { --bg:#1b1b1b; --panel:#2a2a2a; --edge:#0d0d0d; --hi:#00ffc8; --lo:#0ef; --accent:#7fff00; --text:#e6f7f0; --muted:#a8d8cc;
                 font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
                 width: 100%; max-width: none; background: var(--bg); color: var(--text);
                 border: 2px solid #111; box-shadow: inset 0 0 0 1px #333, 0 2px 10px rgba(0,0,0,.4);
                 padding: 8px; border-radius: 6px; user-select: none; }
        .jwamp * { box-sizing: border-box; }
        .jwamp .sr-only { position: absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); border:0; }

        /* Compact header removed; we go straight to the info + controls */
        .jwamp-display { background: #001f1a; border:1px solid #003c33; padding:6px 8px; margin-bottom:6px;
                         color: var(--hi); text-shadow: 0 0 4px rgba(0,255,200,.6); }
        .jwamp-track { display:flex; gap:8px; line-height:1.25; font-size: 13px; flex-wrap: wrap; }
        .jwamp-label { color: var(--muted); min-width: 52px; text-transform: uppercase; font-weight:600; }

        .jwamp-controls {
          display: grid;
          grid-template-columns: auto auto 1fr auto auto;
          gap: 8px;
          align-items: center;
          background: var(--panel);
          border:1px solid var(--edge);
          padding:6px 8px;
          margin-bottom:6px;
        }
        .jwamp-btn { background: #222; color: var(--text); border:1px solid #000; padding:4px 10px; border-radius:4px; cursor:pointer;
                     box-shadow: inset 0 0 0 1px #3a3a3a; font-weight:700; }
        .jwamp-btn:focus { outline: 2px solid var(--lo); outline-offset: 2px; }
        .jwamp-play { min-width: 40px; }
        .jwamp-stop { min-width: 36px; }

        .jwamp-time { min-width: 90px; text-align:center; font-variant-numeric: tabular-nums; color: var(--accent); }
        .jwamp-volume input[type=range] { width: 120px; }
        .jwamp-download { justify-self: end; text-decoration:none; background:#154a40; padding:4px 10px; border-radius:4px; border:1px solid #0c2e28; color: #c6ffe9; }

        .jwamp-progress { position: relative; height: 12px; background: #0b2a24; border:1px solid #08332b; cursor: pointer; border-radius: 3px; width: 100%; }
        .jwamp-bar { position:absolute; top:0; left:0; height:100%; width:0%; background: linear-gradient(90deg, #00ffc8, #0ef); }
        .jwamp-knob { position:absolute; top:-3px; height:18px; width:6px; background:#e6f7f0; box-shadow: 0 0 6px rgba(0,255,200,.8); transform: translateX(-50%); left:0%; border-radius:1px; }

        .jwamp-error { margin-top:6px; color:#ffb3b3; }

        @media (max-width: 520px) {
          .jwamp-controls { grid-template-columns: auto auto 1fr; }
          .jwamp-volume { display: none; }
          .jwamp-download { grid-column: 1 / -1; justify-self: end; }
        }
      CSS

      js = <<~JS
        (function(){
          if (window.JWAMP && window.JWAMP.__booted) return;

          if (!document.getElementById('jekyll-winamp-styles')) {
            var style = document.createElement('style');
            style.id = 'jekyll-winamp-styles';
            style.appendChild(document.createTextNode(#{css.inspect}));
            document.head.appendChild(style);
          }

          function fmt(t){ if(!isFinite(t)||t<0)t=0; var m=Math.floor(t/60), s=Math.floor(t%60); return m+":"+String(s).padStart(2,'0'); }

          function initOne(root){
            if (!root || root.__jwampReady) return;
            root.__jwampReady = true;

            var audio   = root.querySelector('audio');
            var playBtn = root.querySelector('.jwamp-play');
            var stopBtn = root.querySelector('.jwamp-stop');
            var vol     = root.querySelector('#' + root.id + '-vol');
            var curEl   = root.querySelector('#' + root.id + '-current');
            var durEl   = root.querySelector('#' + root.id + '-duration');
            var prog    = root.querySelector('#' + root.id + '-progress');
            var bar     = root.querySelector('#' + root.id + '-bar');
            var knob    = root.querySelector('#' + root.id + '-knob');
            var errEl   = root.querySelector('#' + root.id + '-error');

            function updateProgress(){
              var pct = (audio.currentTime / (audio.duration || 1)) * 100;
              bar.style.width = pct + "%"; knob.style.left = pct + "%";
              curEl.textContent = fmt(audio.currentTime);
              prog.setAttribute('aria-valuenow', String(Math.round(pct)));
            }

            audio.addEventListener('loadedmetadata', function(){ durEl.textContent = fmt(audio.duration); updateProgress(); });
            audio.addEventListener('timeupdate', updateProgress);
            audio.addEventListener('ended', function(){ playBtn.textContent = '▶'; });

            audio.addEventListener('error', function(){
              var code = (audio.error && audio.error.code) || 0;
              errEl.style.display = 'block';
              errEl.textContent = 'Could not load audio (error code ' + code + '). Host may block embedding. Prefer same-origin MP3.';
            });

            playBtn.addEventListener('click', function(){ if(audio.paused){ audio.play(); playBtn.textContent='⏸'; } else { audio.pause(); playBtn.textContent='▶'; } });
            stopBtn.addEventListener('click', function(){ audio.pause(); audio.currentTime=0; playBtn.textContent='▶'; updateProgress(); });

            if (vol) {
              vol.addEventListener('input', function(){ audio.volume = parseFloat(this.value); });
              audio.volume = parseFloat(vol.value || "0.8");
            }

            function setFromClientX(clientX){
              var rect = prog.getBoundingClientRect();
              var x = Math.min(Math.max(clientX - rect.left, 0), rect.width);
              var pct = x / rect.width;
              audio.currentTime = pct * (audio.duration || 0);
            }

            prog.addEventListener('click', function(e){ setFromClientX(e.clientX); });
            prog.addEventListener('mousedown', function(e){
              function move(ev){ setFromClientX(ev.clientX); }
              function up(){ document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up); }
              document.addEventListener('mousemove', move);
              document.addEventListener('mouseup', up);
            });

            root.tabIndex = 0;
            root.addEventListener('keydown', function(e){
              if (e.code === 'Space') { e.preventDefault(); playBtn.click(); }
              else if (e.code === 'ArrowRight') { audio.currentTime = Math.min((audio.currentTime||0)+5, audio.duration||Infinity); }
              else if (e.code === 'ArrowLeft') { audio.currentTime = Math.max((audio.currentTime||0)-5, 0); }
              else if (e.code === 'ArrowUp') { if (vol) { audio.volume = Math.min(audio.volume + 0.05, 1); vol.value = audio.volume.toFixed(2); } }
              else if (e.code === 'ArrowDown') { if (vol) { audio.volume = Math.max(audio.volume - 0.05, 0); vol.value = audio.volume.toFixed(2); } }
            });

            prog.addEventListener('keydown', function(e){
              var step = (audio.duration || 0) * 0.02;
              if (e.code === 'ArrowRight' || e.code === 'ArrowUp') { audio.currentTime = Math.min((audio.currentTime||0)+step, audio.duration||Infinity); e.preventDefault(); }
              if (e.code === 'ArrowLeft'  || e.code === 'ArrowDown') { audio.currentTime = Math.max((audio.currentTime||0)-step, 0); e.preventDefault(); }
              if (e.code === 'Home') { audio.currentTime = 0; e.preventDefault(); }
              if (e.code === 'End')  { audio.currentTime = audio.duration || 0; e.preventDefault(); }
            });
          }

          function initQueued(){
            (window.JWAMPQ || []).forEach(function(selOrEl){
              var el = typeof selOrEl === 'string' ? document.querySelector(selOrEl) : selOrEl;
              if (el) initOne(el);
            });
            window.JWAMPQ = [];
            document.querySelectorAll('.jwamp[data-jwamp]').forEach(initOne);
          }

          window.JWAMP = { __booted: true, initOne: initOne, initAll: initQueued };

          if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initQueued);
          } else {
            initQueued();
          }

          var mo = new MutationObserver(function(muts){
            muts.forEach(function(m){
              m.addedNodes && m.addedNodes.forEach(function(n){
                if (n.nodeType === 1 && n.matches && n.matches('.jwamp[data-jwamp]')) initOne(n);
                if (n.querySelectorAll) n.querySelectorAll('.jwamp[data-jwamp]').forEach(initOne);
              });
            });
          });
          mo.observe(document.documentElement, { childList: true, subtree: true });
        })();
      JS

      <<~HTML
        <script id="jekyll-winamp-boot">#{js}</script>
      HTML
    end
  end

  # PLAYER TAG: markup + enqueue init
  class WinampPlayerTag < Liquid::Tag
    def initialize(tag_name, markup, tokens)
      super
      @src_raw, @opts = WinampHelpers.parse_args(markup)
      @game      = @opts["game"]      || ""
      @title     = @opts["title"]     || ""
      @artist    = @opts["artist"]    || ""
      @year      = @opts["year"]      || ""
      @max_width = @opts["max_width"] || ""
      @autoplay  = %w[true 1 yes].include?((@opts["autoplay"] || "").downcase)
      @loop      = %w[true 1 yes].include?((@opts["loop"] || "").downcase)
      digest_input = [@src_raw, @game, @title, @artist, @year, @autoplay, @loop, @max_width].join("|")
      @id = "jekyll-winamp-#{Digest::MD5.hexdigest(digest_input)[0,8]}"
    end

    def render(context)
      src    = WinampHelpers.unquote(Liquid::Template.parse(@src_raw).render(context)).strip
      return "<!-- jekyll_player: missing mp3 src -->" if src.empty?
      game   = Liquid::Template.parse(@game).render(context)
      title  = Liquid::Template.parse(@title).render(context)
      artist = Liquid::Template.parse(@artist).render(context)
      year   = Liquid::Template.parse(@year).render(context)
      style_attr = @max_width && !@max_width.strip.empty? ? %( style="max-width: #{WinampHelpers.h(@max_width)};") : ""

      <<~HTML
        <div class="jwamp" id="#{@id}" role="region" aria-label="Audio player: #{WinampHelpers.h(title)}" data-jwamp#{style_attr}>
          <audio id="#{@id}-audio"
                 src="#{WinampHelpers.h(src)}"
                 type="audio/mpeg"
                 #{'autoplay' if @autoplay}
                 #{'loop' if @loop}
                 preload="metadata"
                 crossorigin="anonymous"></audio>

          <div class="jwamp-display">
            <div class="jwamp-track"><span class="jwamp-label">Title:</span> <span class="jwamp-value" id="#{@id}-meta-title">#{WinampHelpers.h(title)}</span></div>
            <div class="jwamp-track"><span class="jwamp-label">Game:</span> <span class="jwamp-value" id="#{@id}-meta-game">#{WinampHelpers.h(game)}</span></div>
            #{(artist && !artist.strip.empty?) ? '<div class="jwamp-track"><span class="jwamp-label">Artist:</span> <span class="jwamp-value" id="#{@id}-meta-artist">' + WinampHelpers.h(artist) + '</span></div>' : ''}
            #{(year && !year.strip.empty?) ? '<div class="jwamp-track"><span class="jwamp-label">Year:</span> <span class="jwamp-value" id="#{@id}-meta-year">' + WinampHelpers.h(year) + '</span></div>' : ''}
            <div class="jwamp-error" id="#{@id}-error" style="display:none;"></div>
          </div>

          <div class="jwamp-controls">
            <button class="jwamp-btn jwamp-play" id="#{@id}-play" aria-label="Play/Pause" title="Play/Pause (Space)">▶</button>
            <button class="jwamp-btn jwamp-stop" id="#{@id}-stop" aria-label="Stop" title="Stop">■</button>
            <div class="jwamp-time" aria-live="polite">
              <span id="#{@id}-current">0:00</span> / <span id="#{@id}-duration">0:00</span>
            </div>
            <div class="jwamp-volume">
              <label for="#{@id}-vol" class="sr-only">Volume</label>
              <input type="range" id="#{@id}-vol" min="0" max="1" step="0.01" value="0.8" aria-label="Volume">
            </div>
            <a class="jwamp-download" href="#{WinampHelpers.h(src)}" download title="Download source file" rel="noopener" target="_blank">⬇ Download</a>
          </div>

          <div class="jwamp-progress" id="#{@id}-progress" role="slider" aria-label="Seek" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0" tabindex="0">
            <div class="jwamp-bar" id="#{@id}-bar"></div>
            <div class="jwamp-knob" id="#{@id}-knob" aria-hidden="true"></div>
          </div>

          <noscript>
            <p><em>JavaScript is required for the custom player. You can still <a href="#{WinampHelpers.h(src)}" download>download the MP3</a>.</em></p>
          </noscript>
        </div>
        <script>(window.JWAMPQ=window.JWAMPQ||[]).push('##{@id}');</script>
      HTML
    end
  end
end

Liquid::Template.register_tag("jekyll_player_boot", Jekyll::WinampPlayerBootTag)
Liquid::Template.register_tag("jekyll_player",      Jekyll::WinampPlayerTag)

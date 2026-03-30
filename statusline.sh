#!/bin/bash
# Claude Code Status Line v6

input=$(cat)
echo "$input" > /tmp/claude-statusline-debug.json

# ── Colors ──────────────────────────────────────────
RST='\033[0m'
BOLD='\033[1m'
CYAN='\033[36m'
BCYAN='\033[1;36m'
GREEN='\033[32m'
BGREEN='\033[1;32m'
YELLOW='\033[33m'
BYELLOW='\033[1;33m'
RED='\033[31m'
BRED='\033[1;31m'
BWHITE='\033[1;37m'
WHITE='\033[37m'
GRAY='\033[90m'
MAGENTA='\033[35m'
BMAGENTA='\033[1;35m'
BLUE='\033[34m'
BBLUE='\033[1;34m'

SEP="${CYAN}│${RST}"

# ── Parse JSON ──────────────────────────────────────
eval "$(echo "$input" | jq -r '
  @sh "model=\(.model.display_name // "?")",
  @sh "cwd=\(.workspace.current_dir // .cwd // "")",
  @sh "project_dir=\(.workspace.project_dir // "")",
  @sh "ctx_pct=\(.context_window.used_percentage // "")",
  @sh "ctx_size=\(.context_window.context_window_size // 0)",
  @sh "total_in=\(.context_window.total_input_tokens // 0)",
  @sh "total_out=\(.context_window.total_output_tokens // 0)",
  @sh "cache_write=\(.context_window.current_usage.cache_creation_input_tokens // 0)",
  @sh "cache_read=\(.context_window.current_usage.cache_read_input_tokens // 0)",
  @sh "exceeds_200k=\(.exceeds_200k_tokens // false)",
  @sh "duration_ms=\(.cost.total_duration_ms // 0)",
  @sh "lines_add=\(.cost.total_lines_added // 0)",
  @sh "lines_del=\(.cost.total_lines_removed // 0)",
  @sh "rl_5h=\(.rate_limits.five_hour.used_percentage // "")",
  @sh "rl_5h_reset=\(.rate_limits.five_hour.resets_at // "")",
  @sh "rl_7d=\(.rate_limits.seven_day.used_percentage // "")",
  @sh "rl_7d_reset=\(.rate_limits.seven_day.resets_at // "")",
  @sh "agent_name=\(.agent.name // "")",
  @sh "wt_name=\(.worktree.name // "")",
  @sh "wt_orig_branch=\(.worktree.original_branch // "")"
')"

# ── Helpers ─────────────────────────────────────────

fmt_tokens() {
  local n=$1
  [ -z "$n" ] || [ "$n" = "null" ] && n=0
  if [ "$n" -ge 1000000 ]; then
    awk "BEGIN { printf \"%.1fM\", $n / 1000000 }"
  elif [ "$n" -ge 1000 ]; then
    awk "BEGIN { printf \"%.1fk\", $n / 1000 }"
  else
    echo "$n"
  fi
}

# Always show seconds: 25h16m03s
fmt_duration() {
  local ms=$1
  local total=$((ms / 1000))
  local h=$((total / 3600)) m=$(((total % 3600) / 60)) s=$((total % 60))
  if [ "$h" -gt 0 ]; then printf "%dh %02dm %02ds" "$h" "$m" "$s"
  elif [ "$m" -gt 0 ]; then printf "%dm %02ds" "$m" "$s"
  else printf "%ds" "$s"
  fi
}

fmt_countdown() {
  local ts=$1
  [ -z "$ts" ] || [ "$ts" = "null" ] && return
  local diff=$((ts - $(date +%s)))
  [ "$diff" -le 0 ] && { echo "now"; return; }
  local d=$((diff/86400)) h=$(((diff%86400)/3600)) m=$(((diff%3600)/60))
  if [ "$d" -gt 0 ]; then printf "%dd %dh" "$d" "$h"
  elif [ "$h" -gt 0 ]; then printf "%dh %dm" "$h" "$m"
  else printf "%dm" "$m"
  fi
}

color_pct() {
  local int=$(printf '%.0f' "$1" 2>/dev/null || echo 0)
  local color="$BGREEN"
  [ "$int" -ge 50 ] && color="$BYELLOW"
  [ "$int" -ge 80 ] && color="$BRED"
  printf "${color}%d%%${RST}" "$int"
}

# Stacked context bar: input=cyan, output=yellow, empty=gray
make_context_bar() {
  local width=$1 in_pct=$2 out_pct=$3
  local in_blocks=$(( (in_pct * width + 50) / 100 ))
  local out_blocks=$(( (out_pct * width + 50) / 100 ))
  # Clamp total to width
  if [ $((in_blocks + out_blocks)) -gt "$width" ]; then
    out_blocks=$((width - in_blocks))
  fi
  local empty=$((width - in_blocks - out_blocks))

  local bar=""
  for ((i=0; i<in_blocks; i++)); do bar+="█"; done
  local in_part="$bar"

  bar=""
  for ((i=0; i<out_blocks; i++)); do bar+="█"; done
  local out_part="$bar"

  bar=""
  for ((i=0; i<empty; i++)); do bar+="░"; done
  local empty_part="$bar"

  printf "${WHITE}[${BCYAN}%s${BYELLOW}%s${GRAY}%s${WHITE}]${RST}" "$in_part" "$out_part" "$empty_part"
}

# Rate limit bar with custom color
make_rate_bar() {
  local pct=$1 width=$2 bar_color=$3 bar_bold=$4
  local int=$(printf '%.0f' "$pct" 2>/dev/null || echo 0)
  [ "$int" -gt 100 ] && int=100
  local filled=$(( (int * width + 50) / 100 ))
  [ "$filled" -gt "$width" ] && filled=$width
  local empty=$((width - filled))

  # Override color if danger zone
  local color="$bar_bold"
  [ "$int" -ge 80 ] && color="$BRED"

  local bar="" pad=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do pad+="░"; done

  printf "${WHITE}[${color}%s${GRAY}%s${WHITE}]${RST}" "$bar" "$pad"
}

rate_color_pct() {
  local int=$(printf '%.0f' "$1" 2>/dev/null || echo 0)
  local normal_color=$2
  local color="$normal_color"
  [ "$int" -ge 80 ] && color="$BRED"
  printf "${color}%d%%${RST}" "$int"
}

# ── Derived values ──────────────────────────────────

# Full path with ~ abbreviation for home
clean_cwd=$(echo "$cwd" | tr '\\' '/')
home_unix=$(echo "$HOME" | tr '\\' '/')
display_path="${clean_cwd/#$home_unix/\~}"

# Context breakdown percentages
in_pct=0 out_pct=0
if [ "$ctx_size" -gt 0 ]; then
  [ "$total_in" -gt 0 ] && in_pct=$(awk "BEGIN { printf \"%.0f\", $total_in * 100 / $ctx_size }")
  [ "$total_out" -gt 0 ] && out_pct=$(awk "BEGIN { printf \"%.0f\", $total_out * 100 / $ctx_size }")
fi

# Skip ctx_label if model name already has it
ctx_label=""
if [ "$ctx_size" -ge 1000000 ]; then ctx_label="1M"
elif [ "$ctx_size" -ge 200000 ]; then ctx_label="200k"
fi
model_display="${BCYAN}${model}${RST}"
if [ -n "$ctx_label" ] && ! echo "$model" | grep -qi "context\|${ctx_label}"; then
  model_display+="${CYAN}(${ctx_label})${RST}"
fi

# Git
git_info=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)
  staged=$(git -C "$cwd" --no-optional-locks diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')
  unstaged=$(git -C "$cwd" --no-optional-locks diff --name-only 2>/dev/null | wc -l | tr -d ' ')
  untracked=$(git -C "$cwd" --no-optional-locks ls-files --others --exclude-standard 2>/dev/null | wc -l | tr -d ' ')
  git_info="${BGREEN}${branch}${RST}"
  [ "$staged" -gt 0 ] && git_info+=" ${GREEN}+${staged}${RST}"
  [ "$unstaged" -gt 0 ] && git_info+=" ${YELLOW}~${unstaged}${RST}"
  [ "$untracked" -gt 0 ] && git_info+=" ${WHITE}?${untracked}${RST}"
fi

# ════════════════════════════════════════════════════
# LINE 1: Identity + Path + Activity
# ════════════════════════════════════════════════════
L1="${model_display} ${SEP} ${BWHITE}${display_path}${RST}"

[ -n "$git_info" ] && L1+=" ${SEP} ${git_info}"

# Token counts with context %
in_f=$(fmt_tokens "$total_in")
out_f=$(fmt_tokens "$total_out")
if [ "$total_in" -gt 0 ] || [ "$total_out" -gt 0 ]; then
  tok="${BCYAN}in ${RST}${WHITE}${in_f}${RST}"
  tok+=" ${BYELLOW}out ${RST}${WHITE}${out_f}${RST}"
  L1+=" ${SEP} ${tok}"
fi

# Lines changed
if [ "$lines_add" -gt 0 ] || [ "$lines_del" -gt 0 ]; then
  L1+=" ${SEP} ${GREEN}+${lines_add}${RST} ${RED}-${lines_del}${RST}"
fi

# Duration (always with seconds)
[ "$duration_ms" -gt 0 ] && L1+=" ${SEP} ${WHITE}$(fmt_duration "$duration_ms")${RST}"

# Conditional
if [ -n "$wt_name" ]; then
  wt="${BMAGENTA}wt:${wt_name}${RST}"
  [ -n "$wt_orig_branch" ] && wt+="${MAGENTA}<-${wt_orig_branch}${RST}"
  L1+=" ${SEP} ${wt}"
fi
[ -n "$agent_name" ] && L1+=" ${SEP} ${BYELLOW}agent:${agent_name}${RST}"

echo -e "$L1"

# ════════════════════════════════════════════════════
# LINE 2: Resource Meters
# ════════════════════════════════════════════════════
L2=""

# Context Window — bar + percentage + used/total tokens
if [ -n "$ctx_pct" ]; then
  L2+="${BCYAN}Context Window${RST} $(make_rate_bar "$ctx_pct" 20 "$GREEN" "$BGREEN") $(color_pct "$ctx_pct")"
  [ "$exceeds_200k" = "true" ] && L2+=" ${BRED}[!200k]${RST}"
else
  L2+="${BCYAN}Context Window${RST} ${WHITE}[${GRAY}"
  for ((i=0; i<20; i++)); do L2+="░"; done
  L2+="${WHITE}]${RST} ${GRAY}--%${RST}"
fi

# 5 hours — blue/cyan theme (width 15)
if [ -n "$rl_5h" ]; then
  cd5=$(fmt_countdown "$rl_5h_reset")
  L2+=" ${CYAN}│${RST} ${BBLUE}5 hours${RST} $(make_rate_bar "$rl_5h" 15 "$BLUE" "$BBLUE") $(rate_color_pct "$rl_5h" "$BBLUE")"
  [ -n "$cd5" ] && L2+=" ${WHITE}reset ${cd5}${RST}"
fi

# 7 days — purple/magenta theme (width 15)
if [ -n "$rl_7d" ]; then
  cd7=$(fmt_countdown "$rl_7d_reset")
  L2+=" ${CYAN}│${RST} ${BMAGENTA}7 days${RST} $(make_rate_bar "$rl_7d" 15 "$MAGENTA" "$BMAGENTA") $(rate_color_pct "$rl_7d" "$BMAGENTA")"
  [ -n "$cd7" ] && L2+=" ${WHITE}reset ${cd7}${RST}"
fi

echo -e "$L2"

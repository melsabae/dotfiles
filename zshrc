# Created by newuser for 5.3.1
autoload -Uz compinit promptinit
compinit
promptinit

# The following lines were added by compinstall

zstyle ':completion:*' completer _oldlist _complete _ignored _approximate
zstyle ':completion:*' format 'completing %d'
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' matcher-list '' '+l:|=* r:|=*'
zstyle ':completion:*' max-errors 2 numeric
zstyle ':completion:*' menu select=long
zstyle ':completion:*' preserve-prefix '//[^/]##/'
zstyle ':completion:*' prompt 'found %e errors in completion'
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' squeeze-slashes true
zstyle :compinstall filename '~/.zshrc'

autoload -Uz compinit
compinit
# End of lines added by compinstall

# vi keybound menu selection
zstyle ':completion:*' menu select
zmodload zsh/complist
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history

bindkey -v

source ~/.dotfiles/zsh-git-prompt/zshrc.sh
# non-zero status code
# bold hostname, regular username, prompt and privilege
PROMPT=$'%(?..[%F{red}%?%f] )%F{cyan}%B%m%b%f %F{yellow}%n%f %{\e[5m%}%S>_%#%s %{\e[0m% '

# up to 2 dirs, and status of git repo if available
RPROMPT='%U%2d%u $(git_super_status)'

# spelling correction
setopt CORRECT

# don't redirect-overwrite files
setopt NOCLOBBER

if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias sl='ls'
    alias ll='ls -Altrh --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    # color output even through pipes
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    # less strips color sometimes
    alias less='less -R'

    alias vim.tiny='vim'
    alias vi='vim'
    alias vm='vim'
    alias im='vim'
    alias pythong='py'
    alias py='python2.7'
    alias cls='clear; ls'
    alias cll='clear; ll'
    alias lsl='ls -1 | wc -l'
    alias gcc='gcc -mtune=native -Wall'
    alias calc='gnome-calculator &'
		alias lst='ll -t'
		alias reflector='sudo reflector --verbose --country "United States" -l 20 --sort rate --save /etc/pacman.d/mirrorlist'
		alias pacup='sudo su -c "pacman -Syy; pacman -Syu; pacman -Scc"'
		alias top='htop'
		alias sudp='nocorrect sudo'
fi

HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history
setopt INC_APPEND_HISTORY
setopt EXTENDED_HISTORY
setopt HIST_IGNORE_DUPS
setopt HIST_FIND_NO_DUPS
setopt HIST_IGNORE_ALL_DUPS

# completions go to the end of the completed word
setopt ALWAYS_TO_END

# row-major listings, like any sensible person should use
setopt LIST_ROWS_FIRST

# numbers are numbers, not characters
setopt NUMERIC_GLOB_SORT


bindkey "^[[A" history-beginning-search-backward
bindkey "^[[B" history-beginning-search-forward

autoload -U history-search-end
zle -N history-beginning-search-backward-end history-search-end
bindkey "^[[A" history-beginning-search-backward-end

bindkey '^R' history-incremental-search-backward

man() {
    LESS_TERMCAP_md=$'\e[01;31m' \
    LESS_TERMCAP_me=$'\e[0m' \
    LESS_TERMCAP_se=$'\e[0m' \
    LESS_TERMCAP_so=$'\e[01;44;33m' \
    LESS_TERMCAP_ue=$'\e[0m' \
    LESS_TERMCAP_us=$'\e[01;32m' \
    command man "$@"
}

TERM=xterm

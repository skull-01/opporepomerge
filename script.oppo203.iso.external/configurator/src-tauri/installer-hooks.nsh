; Tauri NSIS PREINSTALL hook for OppoKodiAddon Configurator.
;
; Tauri's own NSIS installer already shows a reinstall page that offers to remove a previously
; installed NSIS version before upgrading. It does NOT see a parallel install of the same product
; made by the *MSI* package. So this hook handles only that gap: it scans the per-machine uninstall
; registry for an MSI install of this product and, if found, offers to remove it first.
;
; Scoping the hook to the MSI case avoids a second, redundant prompt on the common NSIS upgrade
; (where Tauri's reinstall page already asked) -- the user sees one prompt, not two.
;
; NOTE: not unit-testable -- `makensis` validates that this compiles into the installer at build
; time; the actual detect/remove behaviour is operator (Phase-C) verified against a real machine.

!macro NSIS_HOOK_PREINSTALL
  Push $0
  Push $1
  Push $2
  Push $3

  ; $1 = ProductCode (uninstall subkey GUID) of a parallel MSI install of this product; "" if none.
  StrCpy $1 ""
  StrCpy $2 0
  oppo_msi_scan:
    EnumRegKey $3 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" $2
    StrCmp $3 "" oppo_msi_done
    IntOp $2 $2 + 1
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$3" "DisplayName"
    StrCmp $0 "${PRODUCTNAME}" 0 oppo_msi_scan
    ReadRegStr $0 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$3" "Publisher"
    StrCmp $0 "${MANUFACTURER}" 0 oppo_msi_scan
    StrCpy $1 $3
    Goto oppo_msi_done
  oppo_msi_done:

  ; No parallel MSI install -> nothing to do; Tauri's reinstall page handles a prior NSIS version.
  StrCmp $1 "" oppo_pre_done

  MessageBox MB_YESNO|MB_ICONQUESTION "A previous version of ${PRODUCTNAME} installed via the MSI package was found.$\r$\n$\r$\nRemove it before installing? (Recommended)" IDNO oppo_pre_done
    ; $1 holds the matched uninstall subkey name (the MSI ProductCode GUID); remove it silently.
    ExecWait 'msiexec /x $1 /qn /norestart' $2

  oppo_pre_done:
  Pop $3
  Pop $2
  Pop $1
  Pop $0
!macroend

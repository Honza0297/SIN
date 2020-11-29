# Projekt do predmetu SIN

Autor: Jan Beran (xberan43)

UPOZORNENI: Projekt nelze nainstalovat, jelikoz se jedna o projekt realizovany na realnem hardware.
Podrobnejsi informace v dokumentaci.

## Zadani projektu (jedna se o individualni zadani dohodnute e-mailem, zadani jsem tedy zformuloval sam na jeho zaklade):

Vytvorte subsystem chytre domacnosti. System bude obsahovat alespon tri periferni moduly (ovladani osvetleni, 
mereni teploty a vlhkosti a aktuator pro ovladani okennich zaluzii), centralni jednotku a dashboard pro zobrazovani udaju a ovladani.

System bude mit dale pevne nastavena pravidla, ktera napriklad pri dosazeni urcite teploty zajisti zatazeni zaluzii. 

## Neimplementovane casti zadani

Modul pro ovladani okennich zaluzii byl sice naprogramovan a realne namonovan, ukazalo se ale, ze v provozu nefunguje 
dobre a byl proto zahy odstranen. Jelikoz bez nej nemelo smysl implementovat cast projektu zabyvajici se vytvarenim 
pravidel a akci (nebylo by mozne vytvorit smysluplne pravidlo), tato cast projektu rovnez nebyla implementovana.

## Rozsireni zadani

Nad ramec puvodniho zadani byl k systemu pridan i hlasovy asistent Mycroft (open-source obdoba Google Asistenta nebo Amazon Alexy),
ktery umoznuje hlasem ovladat osvetleni. 

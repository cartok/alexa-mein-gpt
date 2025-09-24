# Alexa - Mein GPT

Dies ist aktuell eine Kopie eines Alexa-hosted skills. Das Projekt sollte umgezogen werden und eigenes CI/CD bekommen, damit eigene AWS resourcen anständig verwendet werden können und man bessere Kontrolle über den code hat. Desweiteren kann man bei Alexa-hosted skills keine Umgebungsvariablen setzen, wesshalb ich für den upload den API Key für OpenAI entfernen musste (s. `lambda/chat_gpt.py`).

Der Skill ist dazu da, um ChatGPT mit Alexa nutzen zu können. Es gibt bereits einige ziemlich ausgereifte Skills dieser Art, dies ist nur ein Versuch Python ein wenig kennenzulernen und etwas mit Alexa und AI zu machen. Ich werde den Skill nicht veröffentlichen. Dazu wären alle unten aufgeführten TODOs notwendig und noch mehr (API Key Registrierung oder SSO wenn das reicht). Außerdem sollte der Skill dann zumindest Englisch unterstützen, d.h. i18n müsste generell implementiert werden. Eventuell würde ich auch ein Feature entwickeln, mit dem Benutzer einfach Feedback zu fehlenden Ausdrücken geben können, damit sie wissen, dass etwas passieren wird. Das müsste aber gegen Missbrauch abgesichert werden. Ich müsste schauen, was es in der Richtung gerade gibt. Zumindest sollte man den Nutzer darüber informieren, dass der Skill anhand der Logdaten kontinuierlich verbessert wird. Dazu ist es notwendig, die Logs selbstständig im eigenen AWS Account zu speichern (CloudWatch Logs) und weitere Vorkehrungen zu treffen.

Der Skill soll einfach und schnell einen Chat mit ChatGPT starte und so kurz wie möglich antworten. Bei Alexa-Skills muss das Standard-Startmuster verwendet werden. D.h. man benötigt: `wake word` `launch command` `skill invocation name`. Zum Beispiel: "Alexa, starte GPT", oder "Alexa, frage GPT ob ...". Im letzten Beispiel ist "ob" ein `Ausdruck` (`utterance`), mit dem letztlich der `chat handler` gestartet werden kann. Die `utterances` benötigen zusätzlich einen `slot`, eine Variable, in der das Gesagte zur Verfügung gestellt wird. Die Einschränkung, dass eine `utterance` nicht nur aus einem `slot` bestehen kann, ist hier ein echtes Problem. Es gibt praktisch unendlich viele Möglichkeiten, Fragen zu stellen. Man sollte hier nicht hingehen und alle Verben kodieren, um möglichst natürlich fragen zu können. Ein weiteres Problem ist, dass die `intent handler` nur die Slot-Werte bekommen, also nicht die Information, welcher `launch command` und welche `utterance` verwendet wurden, so dass in den meisten theoretisch möglichen Kombinationen unvollständige Sätze an ChatGPT gesendet würden. Das System ist grundlegend nicht dafür designed AI gesteuerte aktionen durchzuführen. Stattdessen wird auf feingranulare `intends` gesetzt. Daher werde ich die Möglichkeiten einschränken und wahrscheinlich generische Startkommandos verwenden, die die Fragen grammatikalisch korrekt an ChatGPT übergeben. Wenn ich den skill veröffentlichen würde hätte ich die Möglichkeit `intant launch phrases` festlegen zu können, wodurch ich eigentlich eine komplett andere Lage hätte, man könnte den launch Request umgehen, jedoch ist man auf 5 extra Ausdrücke beschränkt.

Für den Anfang bleibt es bei diesem Skill zunächst bei einem Befehl (`Intent`), der wie oben beschrieben leider ohne die W-Fragen und die häufigsten Verben und andere vorstellbare Kombinationen wie "Computer frage GPT ob ..." auskommen muss. Es gibt also nur wenige `utterances` und man muesste sich auf wenige `launch commands` beschränken. Dies sind die `utterances` mit Beispielen:

- `g. p. t. {input}`: "\[Computer\] \[öffne|starte\] \[GPT\] - \[GPT\]: {Wie hoch ist die Wasserkuppe}"
- `frage {input}`: "\[Computer\] \[öffne|starte\] \[GPT\] - \[Frage\]: {Was soll ich morgen machen}"
- `chat {input}`: "\[Computer\] \[frage\] \[GPT\] \[Chat\] - {Kannst du mir sagen was da los ist}"

Durch testen ist mir aufgefallen, dass man trotzdessen was dokumentiert ist, Alexa dazu bringen kann den `launch intent handler` zu überschreiten und direkt einen `intent handler` anzusteuern. Das funktioniert aber **nicht systematisch**: "\[Computer\] \[starte\] \[GPT\] **und** \[frage\] {...}".

Es ist mir auch aufgefallen, dass andere Skills mit ähnlichen `skill invocation names` durch eben solche verhalten zu Verwechslungen führen können. Daher habe ich den `skill invocation name` des vorläufig auf "Mein GPT" geändert.

## Weitere Probleme

- `CloudWatch Logs` sind so schlecht zu benutzen, dass ich mich in mein persönliches AWS-Konto einloggen sollte, um die Dinge zu beschleunigen. Wenn und wenn möglich die Logs in einer Konsole zu verfolgen.
- Ich musste `python` auf `3.7` downgraden (manuell compilen und im venv linken). In den Alexa-hosted skills wird `3.7.v37` verwendet was etwas eigenes sein muss, da es eigentlich bei `3.7.17` das Ende von `3.7` ist. Aufgefallen ist es mir weil `openai` nicht funktionierte, aber es macht allgemein Sinn die lokal die gleiche Version zu verwenden. Wenn man den Skill selbst im eigenen `AWS Lambda` erstellt, kann man `python 3.11` verwenden. Ich müsste noch git hooks und deployment skripte hinzufügen, damit der workflow nicht kaputt geht.
- Ein weiterer Grund für die selbsttändige Nutzung von `AWS Lambda` ist, dass man ansonsten keine Möglichkeit hat Umgebumgsvariablen zu speichern und in diesem Fall gibt es den API Key für ChatGPT der nicht mit in den code gehört. Sowieso würde ich kompleteten git repo Zugriff haben wollen damit ich gescheit aufräumen kann.
- Ich musste ebenso `urllib3` auf `1.26.18` downgraden weil in der python version von Alexa das `ssl` modul anscheinend zu alt ist und [urllib3 v2 es nicht verwenden kann](https://github.com/urllib3/urllib3/issues/2168). Das war notwendig um `openai` zum laufen zu kriegen.
- Intellisense der `import` Aneweisungen von `ask_sdk_` Paketen funktionierte nicht richtig, manche Funktionen und Klassen die existieren und verwendbar gewesen sind wurden nicht gefunden. Ich weis nicht ob es ein Problem mit den Paketen ist oder mit `Pylance`.
- Auto delegation funktionierte irgendwann nicht mehr, ich habe keine Anung warum und finde keine Lösung
- Reprompting funktioniert ebenfalls nicht und ich habe keine Ahnung warum.

## Workflow

- [Local debugging](https://github.com/alexa/alexa-skills-kit-sdk-for-python/tree/master/ask-sdk-local-debug) auf dem `dev` branch um deployment zeit zu sparen, intellisense verwenden zu können. Wenn man ohne die VSCode extension geht, sollte man gucken dass man den Prozess so startet, dass bei Dateiänderungen der Debugger neu gestartet wird, damit man das nicht ständing manuel tun muss. Am besten man verwendet einen file watcher wie `watchdog` oder eben einfach `bunx nodemon ./lambda/local_debug.py`
- Die `ask-cli` zum testen verwenden, statt die `developer console` im browser d.h. `ask dialog -l de-DE`

### Ein paar gute Links

- [Video training](https://www.youtube.com/watch?v=CzTKDu7Qgjs&list=PLdZn93YfA_1ZP1WFkz6bm08v3zFfWwfGW&index=2)
- [Ask-cli](https://developer.amazon.com/en-US/docs/alexa/smapi/quick-start-alexa-skills-kit-command-line-interface.html)
- [Alexa-hosted skill intro](https://developer.amazon.com/de-DE/docs/alexa/hosted-skills/alexa-hosted-skills-create.html)
- [Alexa session](https://developer.amazon.com/en-US/docs/alexa/custom-skills/manage-skill-session-and-session-attributes.html)
- [Alexa dynamodb](https://developer.amazon.com/de-DE/docs/alexa/hosted-skills/alexa-hosted-skills-session-persistence.html)
- [Alexa python sdk docs](https://developer.amazon.com/de-DE/docs/alexa/alexa-skills-kit-sdk-for-python/overview.html)
- [Alexa built-in intents](https://developer.amazon.com/de-DE/docs/alexa/custom-skills/standard-built-in-intents.html#available-standard-built-in-intents)
- [Amazon Lex docs for custom slot creation](https://docs.aws.amazon.com/lexv2/latest/dg/built-in-slot-number.html)
- [OpenAI create chat API](https://platform.openai.com/docs/api-reference/chat/create)

## TODOs (in Reihenfolge)

- S
  - 8 Sekunden timeout error handling. Zumindest schon mal "Beendet" sagen, damit klar ist wie der status ist.
    - Das ist etwas womit Alexa es meiner Meinung nacht übertrieben hat auf Teufel komm raus, pseudo Intelligenz gebaut, nicht toll. Nutzer sollten das Produkt nicht erst studieren müssen, aber die Herausforderung ist natürlich groß, da man, ultimativ gesehen, nur Sprache als Benutzerschnittstelle hat.
  - Es sollte möglich sein bewusst einzelne Fragen stellen zu können mit dem wissen, dass der Skill danach direkt beendet wird.
- A
  - `poetry` ausprobieren. Vielleicht hat man damit weniger Probleme mit falschen Paket Versionen und man kann scripte erstellen, ansonsten ggf. einfach `package.json` und `bun`.
  - Umziehen auf eigenes git damit man gescheit mit der git history arbeiten kann und um eigenes AWS zu verwenden, erstmal nur lambda, CI/CD.
  - Testing aller Moeglichkeiten mit einem einfachen Grundszenario
    - Per JSON file?
    - Sinnvoll automatisierbar?
- B
  - Refactoring: Ein Ordner pro custom intent.
  - Refactorring: `chat_gpt.py` würde mit mehr OOP besser aussehen und im Umgang fehlerunanfälliger sein.
  - i18n und informationen aus den model definitionen in `skill-package/interactionModels` verwenden um Antworten von Alexa zu bilden, die z. B. den Skill namen beinhalten.
  - Herausfinden ob es möglich ist im `CancelIntentHandler` (bzw. allgemein) herauszufinden welcher der vorherige Intent gewesen ist. Ich glaube aber es gibt halt einfach keinen `context` sondern nur `requests`. Ich könnte ggf. einen interceptor erstellen der jeden intent auf session Dauer in ein array speichert, oder eben nur den letzten und den aktuellen. Das kann es eigentlich echt nicht sein, ärgerlich...
  - Ich bin mir ehrlich gesagt nicht ganz sicher was der Vorteil dabei ist die Nachrichten in der session zu speichern. Es würde ebenso gehen sie in einem Python Objekt (in dem runtime prozess zu speichern), ist es möglich das dabei etwas schieflaufen kann, wenn auch selten?
- C
  - Ermögliche mehrere chats
  - Die Länge der Antwort sollte ggf. anpassbar sein (erhöhen \[verdoppeln\] & setzen \[kurz,mittel,lang\])
  - `AMAZON.FallbackIntent` testen
  - DynamoDB nutzen um die d dauerhaft zu speichern
  - Features hinzufügen (DRAFT):
    - Chats automatisch Titel geben (generiert per GPT)
    - Alle chats abrufbar machen (Index und Titel vorlesen)
    - Alle chats löschen
    - Aktuellen chat löschen
    - Aktuellen chat umbennennen
  - Auf für mehrere Nutzer verwendbar machen. Einfache Bedienung!
  - Chats per AI in grobe Themen einordnen und darüber ansteuerbar machen
  - Themen erstellbar machen, wie zum Beispiel "Kochen" und es ermöglichen chats darin einzuordnen
- D
  - Für die Erfahrung einen Webservice erstellen, hosten, verwenden und ggf. JS SDK und bun als runtime verwenden (refactoring)

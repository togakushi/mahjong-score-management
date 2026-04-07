利用APIと要求権限
=================

Bot Token Scopes
----------------

.. list-table::
   :width: 100%
   :header-rows: 1
   :stub-columns: 1

   * - Scope
     - chat_postMessage
     - files_upload_v2
     - | reactions_add
       | reactions_remove
     - reactions_get
     - conversations_open
     - conversations_replies
     - bot events
     - その他
   * - commands
     -
     -
     -
     -
     -
     -
     -
     - Slash Commands
   * - channels:history
     -
     -
     -
     -
     -
     - |:/:|
     - message.channels
     -
   * - groups:history
     -
     -
     -
     -
     -
     - |:/:|
     - message.groups
     -
   * - chat:write
     - |:/:|
     -
     -
     -
     -
     -
     -
     -
   * - files:write
     -
     - |:/:|
     -
     -
     -
     -
     -
     -
   * - im\:history
     -
     -
     -
     -
     -
     - |:/:|
     - message.im
     -
   * - im\:write
     -
     -
     -
     -
     - |:/:|
     -
     -
     -
   * - reactions:read
     -
     -
     -
     - |:/:|
     -
     -
     -
     -
   * - reactions:write
     -
     -
     - |:/:|
     -
     -
     -
     -
     -
   * - reactions:write
     -
     -
     -
     -
     -
     -
     - app_home_opened
     -


OAuth Scope
-----------

.. list-table::
   :width: 100%
   :widths: 20 80
   :header-rows: 1
   :stub-columns: 1

   * - Scope
     - search_messages
   * - search:read
     - |:/:|

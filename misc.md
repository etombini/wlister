From [mod_python JIRA - MODPYTHON-129 - 2006-11-21](https://issues.apache.org/jira/browse/MODPYTHON-129?focusedCommentId=12451819&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-12451819)  
**Graham Dumpleton added a comment - 21/Nov/06 23:33**

From a bit of discussion on mailing list, have come to conclusion that how
content handlers are treated should stay the same. For other phases,
should be made to work how Apache does things. Final summary post
from mailing list below.

Okay, I think I have a good plan now.

To summarise the whole issue, the way Apache treats multiple handlers in
a single phase for non content handler phases is as follows:

PostReadRequestHandler RUN_ALL
TransHandler RUN_FIRST
MapToStorageHandler RUN_FIRST
InitHandler RUN_ALL
HeaderParserHandler RUN_ALL
AccessHandler RUN_ALL
AuthenHandler RUN_FIRST
AuthzHandler RUN_FIRST
TypeHandler RUN_FIRST
FixupHandler RUN_ALL

LogHandler RUN_ALL

RUN_ALL means run all handlers until one returns something other than OK
or DECLINED. Thus, handler needs to return DONE or an error to have it stop
processing for that phase.

RUN_FIRST means run all handlers while they return DECLINED. Thus, needs
handler to return OK, DONE or error to have it stop processing for that phase.

Where multiple handlers are registered within mod_python for a single
phase it doesn't behave like either of these. In mod_python it will keep
running the handlers only while OK is returned. Returning DECLINED
causes it to stop. This existing behaviour can be described (like mod_perl)
as stacked handlers.

Having non content handler phases behave differently to how Apache does
it causes problems. For example things like a string of authentication
handlers which only say OK when they handle the authentication type,
can't be implemented properly. In Apache, it should stop the first time
one returns OK, but in mod_python it will keep running the handlers
in that phase.

In summary, it needs to behave more like Apache for the non content
handler phases.

In respect of the content handler phase itself, in practice only one handler
module is supposed to implement it. At the Apache level there is no
concept of different Apache modules having goes at the content handler
phase and returning DECLINED if they don't want to handle it. This is
reflected in how in the type handler phase, selection of the module to
deliver content is usually done by setting the single valued req.handler
string. Although, when using mod_python this is done implicitly by
setting the SetHandler/AddHandler directives and mod_negotiation then
in turn setting req.handler to be mod_python for you.

Because mod_python when executed for the content handler phase is
the only thing generating the content, the existing mechanism of
stacked handlers and how the status is handled is fine within just
the content handler phase. Can thus keep that as is and no chance of
stuffing up existing systems.

Where another phase calls req.add_handler() to add a handler or multiple
handlers for the "PythonHandler" (content) phase, these will be added in
a stacked manner within that phase. This also is the same as it works now.
There would be non need to have a new function to add stacked handlers
as that behaviour would be dictated by phase being "PythonHandler".

For all the non content handler phases though, the current stacked
handlers algorithm used by mod_python would be replaced with how
Apache does it. That is, within multiple handlers registered with mod_python
for non content handler phase, it would use RUN_FIRST or RUN_ALL
algorithm as appropriate for the phase.

For those which use RUN_ALL, this wouldn't be much different than what
mod_python does now except that returning DECLINED would cause it
to go to next mod_python handler in that phase instead of stopping.
It is highly unlikely that this change would have an impact as returning
DECLINED in RUN_ALL phases for how mod_python currently implements
it, tends not to be useful and can't see that anyone would have been using it.

For those which use RUN_FIRST, the difference would be significant as
reurning OK will now cause it to stop instead of going to next mod_python
handler in the phase. Personally I don't think this would be a drama as
not many people would be using these phases and highly unlikely that
someone would have listed multiple handlers for such phases. If they had
and knew what they were doing, they should have long ago realised that
the current behaviour was a bit broken and it even probably stopped them
from doing what they wanted unless they fudged it.

As to use of req.add_handler() for non content handler phases, each call
would create a distinct handler, ie., no stacking of handlers at all. No
separate function is required though, as slight change in behaviour
determine form phase specified.

To sum up, I think these changes would have minimal if no impact as
where changes are significant, it isn't likely to overlap with existing code
as shortcomings in current system would have mean't people wouldn't
have been doing the sorts of things that may have been impacted.

Therefore, I don't see a need for this to be switch enabled and the
change could just be made and merely documented.

Luckily the changes to make it work like above should be fairly easy. All
it will entail is changing CallBack.HandlerDispatch() to treat status
differently dependent on phase. No changes to req.add_handler() or
code processing directives will be required.

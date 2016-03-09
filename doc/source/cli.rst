CLI Commands
============

DCI CLI commands are run via the ``dcictl`` console application, which you can
install via the ``python2-dciclient`` or ``python3-dciclient`` (depending on
the version of Python you're running locally).

Updating Resources
------------------

It is useful to understand how the REST API works on the DCI Control-Server,
so that if you need to update resources via the console, you can do so
successfully.

Resource identity and entity tags
---------------------------------

Resources that can be updated contain both an ``ID`` field, and an ``ETag``
field. When updating a resource you need to pass both the ``ID`` and ``ETag``
values before the API will allow you to update that resource.

The ``ID`` field is the unique identifier of the resource you are looking to
update. You will reference this ``ID`` value when also looking up information
for a resource. For example, if you needed to look up information about a team,
then you could run ``dcictl team-show --id <UUID>``, and information about the
team with the ID you passed to the API server would be returned.

Part of the information returned would be the ``etag`` or *Entity Tag*. An
entity tag is a unique hash representing the data of the resource. The value of
the entity tag changes each time the resource is updated.

The purpose of the entity tag is to avoid multiple changes overwriting each
other, allowing for basic concurrency control when you have multiple
application servers behind a load balancer (for instance). On the API server,
every update is performed as a transaction. If multiple requests are received
at nearly the same time, your update will fail, and another lookup of the
entity tag will be required.

If interacting with the API directly, this can be dealt with via the
``If-Match`` header, described at
`http://www.restpatterns.org/HTTP_Headers/If-Match
<http://www.restpatterns.org/HTTP_Headers/If-Match>`_


.. toctree::
   :maxdepth: 2

   component
   file
   jobdefinition
   job
   jobstate
   remoteci
   team
   test
   topic
   user

"""
Example: Deploying a Django REST Framework application as an MCP server.

This example shows how to deploy a Django REST Framework application
using the Tadata SDK. This is a complete working example that sets up
a minimal Django configuration with drf-spectacular.
"""

import os
import django
from django.conf import settings
from tadata_sdk import deploy


def setup_django():
    """Set up a minimal Django configuration for demonstration."""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            SECRET_KEY="demo-secret-key-not-for-production",
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "rest_framework",
                "drf_spectacular",
            ],
            REST_FRAMEWORK={
                "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
            },
            SPECTACULAR_SETTINGS={
                "TITLE": "Demo Django API",
                "DESCRIPTION": "A demonstration Django REST Framework API",
                "VERSION": "1.0.0",
            },
            ROOT_URLCONF=__name__,  # Use this module as the URL config
            USE_TZ=True,
        )
        django.setup()


def create_demo_api():
    """Create a simple Django REST API for demonstration."""
    from django.urls import path, include
    from rest_framework import serializers, viewsets, routers
    from rest_framework.decorators import api_view
    from rest_framework.response import Response

    # Simple serializer
    class ItemSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField(max_length=100)
        description = serializers.CharField(max_length=500, required=False)

    # Simple viewset
    class ItemViewSet(viewsets.ViewSet):
        """A simple ViewSet for managing items."""

        def list(self, request):
            """List all items."""
            items = [
                {"id": 1, "name": "Item 1", "description": "First item"},
                {"id": 2, "name": "Item 2", "description": "Second item"},
            ]
            serializer = ItemSerializer(items, many=True)
            return Response(serializer.data)

        def retrieve(self, request, pk=None):
            """Retrieve a specific item."""
            item = {"id": int(pk), "name": f"Item {pk}", "description": f"Item number {pk}"}
            serializer = ItemSerializer(item)
            return Response(serializer.data)

    # Simple API view
    @api_view(["GET"])
    def hello_world(request):
        """A simple hello world endpoint."""
        return Response({"message": "Hello from Django!"})

    # Setup URL routing
    router = routers.DefaultRouter()
    router.register(r"items", ItemViewSet, basename="item")

    # URL patterns (this module serves as ROOT_URLCONF)
    global urlpatterns
    urlpatterns = [
        path("api/", include(router.urls)),
        path("hello/", hello_world, name="hello"),
    ]


def main():
    """Deploy Django REST Framework application."""
    print("Setting up Django configuration...")
    setup_django()

    print("Creating demo API...")
    create_demo_api()

    print("Django setup complete! Now deploying to Tadata...")

    # Get API key (you would set this in your environment)
    api_key = os.getenv("TADATA_API_KEY")
    if not api_key:
        print("⚠️  TADATA_API_KEY environment variable not set.")
        print("   For a real deployment, you would need to set this.")
        print("   For this demo, we'll show what the call would look like:")
        print()
        print("   result = deploy(")
        print("       use_django=True,")
        print("       api_key='your-api-key-here',")
        print("       name='my-django-api',")
        print("       base_url='https://api.example.com'")
        print("   )")
        print()
        print("Let's test the Django schema extraction instead...")

        # Test the schema extraction without actually deploying
        from tadata_sdk.openapi.source import OpenAPISpec

        try:
            spec = OpenAPISpec.from_django()
            print("✅ Django schema extraction successful!")
            print(f"   API Title: {spec.info.title}")
            print(f"   API Version: {spec.info.version}")
            print(f"   Available paths: {list(spec.paths.keys())}")
            print()
            print("This OpenAPI specification would be deployed to Tadata as an MCP server.")
        except Exception as e:
            print(f"❌ Schema extraction failed: {e}")
        return

    # Deploy using Django schema extraction
    try:
        result = deploy(
            use_django=True,  # Extract schema from configured Django application
            api_key=api_key,
            base_url="https://api.example.com",  # Your Django API base URL
        )

        print("✅ Deployment successful!")
        print(f"   MCP Server ID: {result.id}")
        print(f"   Created at: {result.created_at}")
        if result.updated:
            print("   Status: New deployment created")
        else:
            print("   Status: No changes detected, deployment skipped")

    except Exception as e:
        print(f"❌ Deployment failed: {e}")


if __name__ == "__main__":
    main()

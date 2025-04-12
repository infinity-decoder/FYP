# just a simple context processor to add user files to the context , as i do not want to pass it from every view
from .models import PcapFile

def user_files(request):
    """
    Context processor that adds the user's uploaded files to every template context.
    
    Returns:
        dict: Contains 'user_files' queryset if user is authenticated, empty dict otherwise.
    """
    if request.user.is_authenticated:
        return {
            'user_files': PcapFile.objects.filter(
                user=request.user
            ).order_by('-uploaded_at')[:10]  # Only show 10 most recent files
        }
    return {}  # Return empty dict for non-authenticated users
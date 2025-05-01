# webapp/IDS/context_processors.py

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
            ).order_by('-uploaded_at').only(
                'id', 'file', 'uploaded_at', 'status', 
                'progress_stage', 'progress_message'
            )[:10]  # Only show 10 most recent files
        }
    return {}  # Return empty dict for non-authenticated users
from django.shortcuts import render, get_object_or_404, redirect
from .forms import MoveForm
from .models import Character, Equipement
from django.http import JsonResponse

def post_list(request):
    characters = Character.objects.all()
    equipements = Equipement.objects.all()
    return render(request, 'blog/post_list.html', {'characters': characters, 'equipements': equipements})

def correspondance(character_etat, nouveau_lieu):
    if character_etat == "prete" and nouveau_lieu == "piste":
        return True
    elif character_etat == "cassee" and nouveau_lieu == "garage":
        return True
    elif character_etat == "sale" and nouveau_lieu == "station_lavage":
        return True
    elif character_etat == "en panne" and nouveau_lieu == "station_essence":
        return True
    else:
        return False


def maj_etat_interne(character, place):
    if place.id_equip == "garage":
        character.etat = "sale"
    elif place.id_equip == "piste":
        character.etat = "cassee"
    elif place.id_equip == "station_lavage":
        character.etat = "en panne"
    elif place.id_equip == "station_essence":
        character.etat = "prete"
    character.save()

def maj_etat(request, character_id, place_id):
    character = get_object_or_404(Character, id_character=character_id)
    place = get_object_or_404(Equipement, id_equip=place_id)
    maj_etat_interne(character, place)
    return JsonResponse({'status': 'success'})

def maj_disponibilite(place):
    if place.id_equip == "piste":
        place.disponibilite = "libre"
    elif place.id_equip in ["sation_lavage", "garage", "station_essence"]:
        place.disponibilite = "occupé"
    place.save()

def post_detail(request, id_character):
    character = get_object_or_404(Character, id_character=id_character)
    message = ""
    error = None
    form = MoveForm(request.POST, instance=character)
    ancien_lieu = get_object_or_404(Equipement, id_equip=character.lieu.id_equip)
    if request.method == "POST" and form.is_valid():
        form.save()
        nouveau_lieu = get_object_or_404(Equipement, id_equip=character.lieu.id_equip)
        if nouveau_lieu.disponibilite == "libre" and correspondance(character.etat, nouveau_lieu.id_equip):
            error = False
            ancien_lieu.disponibilite = "libre"
            maj_disponibilite(nouveau_lieu)
            ancien_lieu.save()
            form.save()
            correspondance(character, nouveau_lieu)
            message = "Modification bien enregistrée."
        else:
            message = "Modification impossible."
            error = True
        return render(request,
                  'blog/post_detail.html',
                  {'character': character, 'message': message, 'error': error, 'lieu': ancien_lieu, 'new_lieu':nouveau_lieu, 'form': form})
    else:
        form = MoveForm()
        return render(request,
                  'blog/post_detail.html',
                  {'character': character, 'message': message, 'lieu': ancien_lieu, 'form': form})
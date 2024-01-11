import os
from dotenv import load_dotenv
import supervisely as sly
from collections import defaultdict
from typing import List, Dict, Tuple

# load ENV variables for debug
# has no effect in production
if sly.is_development:
    load_dotenv(os.path.expanduser("~/supervisely.env"))
    load_dotenv("local.env")

grouping_mode = os.environ["modal.state.selectOption"]
batch_size = int(os.environ["modal.state.sliderValue"])
no_batches_mode = bool(os.environ["modal.state.noBatches"])
if no_batches_mode:
    grouping_mode = "by-batches"

grouped_dict = defaultdict(list)


def add_batch_to_grouped_dict(image_ids: List[int], anns: List[sly.Annotation]) -> None:
    if grouping_mode == "by-batches":
        grouped_dict["group"].extend(list(zip(image_ids, anns)))
    for image_id, ann in zip(image_ids, anns):
        entry = (image_id, ann)
        if grouping_mode == "obj-class":
            for label in ann.labels:
                if entry not in grouped_dict[label.obj_class.name]:
                    grouped_dict[label.obj_class.name].append(entry)
        elif grouping_mode == "tags":
            for tag in ann.img_tags:
                if entry not in grouped_dict[tag.name]:
                    grouped_dict[tag.name].append(entry)
    if len(grouped_dict.keys()) == 0:
        sly.logger.warning(
            "There are no instances of annotations for the grouping mode you have selected. Thus, no tags will be added."
        )


def extract_batches(batch_size):
    for group_name in list(grouped_dict.keys()):
        while len(grouped_dict[group_name]) >= batch_size:
            batch = grouped_dict[group_name][:batch_size]
            grouped_dict[group_name] = grouped_dict[group_name][batch_size:]
            yield (group_name, batch)


def process_batches(
    anns_dict: Dict,
    batch: Tuple[str, List[Tuple[int, sly.Annotation]]],
    group_index: int,
    tag_meta_group: sly.TagMeta,
):
    group_name, group_data = batch
    if not group_data:
        return anns_dict
    for im_id, im_ann in group_data:
        tag = sly.Tag(tag_meta_group, f"{group_name}_{group_index}")
        if im_id in anns_dict:
            im_ann = anns_dict[im_id]
        anns_dict[im_id] = im_ann.add_tag(tag)
    return anns_dict


def get_free_tag_name(original_string: str, names_list: List[str]):
    if original_string in names_list:
        counter = 1
        new_string = f"{original_string}_{counter}"
        while new_string in names_list:
            counter += 1
            new_string = f"{original_string}_{counter}"
        return new_string
    else:
        return original_string


@sly.handle_exceptions
def main():
    api = sly.Api.from_env()
    task_id = sly.env.task_id()
    project_id = sly.env.project_id(raise_not_found=False)
    dataset_id = sly.env.dataset_id(raise_not_found=False)
    if project_id is None:
        dataset_info = api.dataset.get_info_by_id(dataset_id)
        project_id = dataset_info.project_id
        datasets = [dataset_info]
    else:
        project = api.project.get_info_by_id(project_id)
        datasets = api.dataset.get_list(project.id)

    # Add tag meta and check if tag with given name already exists
    project_meta = sly.ProjectMeta.from_json(api.project.get_meta(project_id))
    tag_meta_names = [tag_m.name for tag_m in project_meta.tag_metas]
    tag_name = get_free_tag_name("group_id", tag_meta_names)

    # Add and update tag meta
    tag_meta_group = sly.TagMeta(name=tag_name, value_type=sly.TagValueType.ANY_STRING)
    api.project.update_meta(project_id, project_meta.add_tag_meta(tag_meta_group))

    # Enable multi-tag mode and grouping
    api.project.update_settings(project_id, settings={"allowDuplicateTags": True})
    api.project.images_grouping(project_id, enable=True, tag_name=tag_name)
    sly.logger.info(
        f"Successfully updated project's settings, and enabled images grouping by the tag {tag_name}"
    )

    # Get list of datasets and iterate over it
    progress = sly.Progress(message=f"Processing datasets...", total_cnt=len(datasets))
    for dataset in datasets:
        # Get list of all the images and their ids in a dataset
        images = api.image.get_list(dataset.id)
        image_ids = [img.id for img in images]
        group_index = 1
        annotations_for_upload = {}
        # Download all image annotations
        sly.logger.info(f"{len(image_ids)} images are ready to be downloaded and processed...")
        for batched_image_ids in sly.batched(image_ids):
            anns_json = api.annotation.download_json_batch(
                dataset_id=dataset.id, image_ids=batched_image_ids
            )
            anns = [sly.Annotation.from_json(ann_json, project_meta) for ann_json in anns_json]
            add_batch_to_grouped_dict(batched_image_ids, anns)  # Generate a map
            # Iterate over the map, and build a dict with ready-to-upload annotations
            if no_batches_mode:
                batch_size = len(images)
            for batch in extract_batches(batch_size):
                annotations_for_upload = process_batches(
                    annotations_for_upload, batch, group_index, tag_meta_group
                )
                group_index += 1
        for unfinished_batch in grouped_dict.items():  # Process batch residue
            annotations_for_upload = process_batches(
                annotations_for_upload, unfinished_batch, group_index, tag_meta_group
            )
        grouped_dict.clear()
        sly.logger.info(
            f"Total of {len(annotations_for_upload.values())} images are processed and prepared for upload"
        )
        image_ids_list = list(annotations_for_upload.keys())
        annotations_list = list(annotations_for_upload.values())

        # Upload the updated annotations in batches
        for batched_ids, batched_anns in zip(
            sly.batched(image_ids_list), sly.batched(annotations_list)
        ):
            api.annotation.upload_anns(batched_ids, batched_anns)
        sly.Progress.iter_done_report(progress)
    api.task.set_output_project(task_id, project_id, project.name)


if __name__ == "__main__":
    main()
